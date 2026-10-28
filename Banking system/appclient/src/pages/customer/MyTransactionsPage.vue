<template>
  <q-page>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Transactions</div>
    </div>

    <div class="row q-col-gutter-lg q-mb-lg">
      <div class="col-12 col-sm-4">
        <div class="bank-card tx-sum">
          <div class="bank-icon-tile tx-tile--in"><q-icon name="south_west" size="22px" /></div>
          <div>
            <div class="text-caption">Money in</div>
            <div class="tx-sum__amount bank-amount text-credit">+₱{{ format(totals.in) }}</div>
          </div>
        </div>
      </div>
      <div class="col-12 col-sm-4">
        <div class="bank-card tx-sum">
          <div class="bank-icon-tile tx-tile--out"><q-icon name="north_east" size="22px" /></div>
          <div>
            <div class="text-caption">Money out</div>
            <div class="tx-sum__amount bank-amount text-debit">-₱{{ format(totals.out) }}</div>
          </div>
        </div>
      </div>
      <div class="col-12 col-sm-4">
        <div class="bank-card tx-sum">
          <div class="bank-icon-tile tx-tile--count"><q-icon name="receipt_long" size="22px" /></div>
          <div>
            <div class="text-caption">Transactions</div>
            <div class="tx-sum__amount bank-amount">{{ rows.length }}</div>
          </div>
        </div>
      </div>
    </div>

    <q-table
      :rows="rows"
      :columns="columns"
      :filter="search"
      row-key="key"
      :loading="loading"
      flat
      bordered
      no-data-label="No transactions yet"
      :pagination="{ sortBy: 'date', descending: true, rowsPerPage: 15 }"
    >
      <template #top-right>
        <q-input v-model="search" dense outlined clearable placeholder="Search" aria-label="Search transactions">
          <template #append><q-icon name="search" /></template>
        </q-input>
      </template>
      <template #body-cell-type="props">
        <q-td :props="props">
          <div class="row items-center no-wrap q-gutter-x-sm">
            <div class="tx-dir" :class="props.row.direction === 'credit' ? 'tx-tile--in' : 'tx-tile--out'">
              <q-icon :name="props.row.direction === 'credit' ? 'south_west' : 'north_east'" size="16px" />
            </div>
            <span class="text-weight-medium">{{ typeLabel(props.row.type) }}</span>
          </div>
        </q-td>
      </template>
      <template #body-cell-date="props">
        <q-td :props="props" class="bank-cell-date">{{ formatDate(props.row.date) }}</q-td>
      </template>
      <template #body-cell-amount="props">
        <q-td :props="props" class="text-weight-bold" :class="props.row.direction === 'credit' ? 'text-credit' : 'text-debit'">
          {{ props.row.direction === 'credit' ? '+' : '-' }}₱{{ format(props.row.amount) }}
        </q-td>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'
import { errorMessage } from '@/utils/notify-error'
import { formatDate } from '@/utils/tableColumns'

// Same as REFUNDED_STATUSES in the backend's interbank_transfers router.
const REFUNDED_STATUSES = ['FAILED', 'REVERSED']

const $q = useQuasar()
const rows = ref([])
const search = ref('')
const loading = ref(true)

const columns = [
  { name: 'type', label: 'Transaction', field: 'type', align: 'left' },
  { name: 'date', label: 'Date', field: 'date', align: 'left', sortable: true },
  { name: 'account_number', label: 'Account', field: 'account_number', align: 'left' },
  { name: 'reference', label: 'Reference', field: 'reference', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
]

function format (val) {
  return Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function typeLabel (type) {
  return {
    DEPOSIT: 'Deposit',
    WITHDRAWAL: 'Withdrawal',
    'TRANSFER OUT': 'Transfer sent',
    'TRANSFER IN': 'Transfer received',
    INTERBANK: 'Interbank transfer',
    OPENING: 'Opening deposit',
    FEE: 'Bank fee',
    INTEREST: 'Interest earned',
  }[type] || type
}

const totals = computed(() => rows.value.reduce((t, r) => {
  t[r.direction === 'credit' ? 'in' : 'out'] += Number(r.amount)
  return t
}, { in: 0, out: 0 }))

onMounted(async () => {
  try {
    // The backend only returns the customer's own accounts and transactions;
    // the ids are still needed to tell money in from money out on transfers.
    const { data: allAccounts } = await api.get('/accounts/')
    const myAccountIds = allAccounts.map((a) => a.id)
    const accountNumberById = Object.fromEntries(allAccounts.map((a) => [a.id, a.account_number]))

    const [deposits, withdrawals, transfers, interbank, fees, interest, ledger] = await Promise.all([
      api.get('/deposits/'),
      api.get('/withdrawals/'),
      api.get('/transfers/'),
      api.get('/interbank-transfers/'),
      api.get('/fee-records/'),
      api.get('/interest-records/'),
      api.get('/ledger-entries/'),
    ])

    const combined = []

    for (const d of deposits.data) {
      // A pending or rejected deposit hasn't put money in the account.
      if (myAccountIds.includes(d.account_id) && d.status === 'COMPLETED') {
        combined.push({
          key: `dep-${d.id}`,
          date: d.transaction_date,
          type: 'DEPOSIT',
          account_number: accountNumberById[d.account_id],
          reference: d.reference_number,
          amount: d.amount,
          direction: 'credit',
        })
      }
    }

    for (const w of withdrawals.data) {
      if (myAccountIds.includes(w.account_id)) {
        combined.push({
          key: `wd-${w.id}`,
          date: w.transaction_date,
          type: 'WITHDRAWAL',
          account_number: accountNumberById[w.account_id],
          reference: w.reference_number,
          amount: w.amount,
          direction: 'debit',
        })
      }
    }

    for (const t of transfers.data) {
      if (myAccountIds.includes(t.source_account_id)) {
        combined.push({
          key: `trf-out-${t.id}`,
          date: t.created_at,
          type: 'TRANSFER OUT',
          account_number: accountNumberById[t.source_account_id],
          reference: t.transfer_reference,
          amount: t.amount,
          direction: 'debit',
        })
      }
      if (myAccountIds.includes(t.destination_account_id)) {
        combined.push({
          key: `trf-in-${t.id}`,
          date: t.created_at,
          type: 'TRANSFER IN',
          account_number: accountNumberById[t.destination_account_id],
          reference: t.transfer_reference,
          amount: t.amount,
          direction: 'credit',
        })
      }
    }

    for (const i of interbank.data) {
      // FAILED and REVERSED transfers were refunded (amount + fee came back),
      // so they are not money out.
      if (myAccountIds.includes(i.source_account_id) && !REFUNDED_STATUSES.includes(i.status)) {
        combined.push({
          key: `ibt-${i.id}`,
          date: i.initiated_at,
          type: 'INTERBANK',
          account_number: accountNumberById[i.source_account_id],
          reference: i.reference_number,
          amount: Number(i.amount) + Number(i.transfer_fee),
          direction: 'debit',
        })
      }
    }

    // Fees and interest also change the balance, so they belong here too
    // (otherwise "money in - money out" doesn't match the balance).
    for (const f of fees.data) {
      if (myAccountIds.includes(f.account_id)) {
        combined.push({
          key: `fee-${f.id}`,
          date: f.charged_at,
          type: 'FEE',
          account_number: accountNumberById[f.account_id],
          reference: f.transaction_reference || `FEE-${f.id}`,
          amount: f.amount_charged,
          direction: 'debit',
        })
      }
    }

    // An account type's opening deposit has no deposits row; it is only in
    // the ledger, as the account's first entry (reference OPEN-<account number>).
    for (const l of ledger.data) {
      if (myAccountIds.includes(l.account_id) && l.transaction_reference === `OPEN-${accountNumberById[l.account_id]}`) {
        combined.push({
          key: `open-${l.id}`,
          date: l.transaction_date,
          type: 'OPENING',
          account_number: accountNumberById[l.account_id],
          reference: l.transaction_reference,
          amount: l.credit_amount,
          direction: 'credit',
        })
      }
    }

    for (const r of interest.data) {
      if (myAccountIds.includes(r.account_id)) {
        combined.push({
          key: `int-${r.id}`,
          date: r.credited_at,
          type: 'INTEREST',
          account_number: accountNumberById[r.account_id],
          reference: `INT-${r.id}`,
          amount: r.amount_credited,
          direction: 'credit',
        })
      }
    }

    combined.sort((a, b) => new Date(b.date) - new Date(a.date))
    rows.value = combined
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load transactions') })
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.tx-sum {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
}

.tx-sum__amount {
  font-size: 1.4rem;
  line-height: 1.2;
}

.tx-dir {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.tx-tile--in { background: var(--tipon-sea-tint); color: var(--bank-credit); }
.tx-tile--out { background: var(--tipon-bad-tint); color: var(--bank-debit); }
.tx-tile--count { background: var(--tipon-ink-tint); color: var(--tipon-ink); }
</style>
