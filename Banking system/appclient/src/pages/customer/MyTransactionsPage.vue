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
import api from '@/services/api'
import { formatDate } from '@/utils/tableColumns'

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

    const [deposits, withdrawals, transfers, interbank] = await Promise.all([
      api.get('/deposits/'),
      api.get('/withdrawals/'),
      api.get('/transfers/'),
      api.get('/interbank-transfers/'),
    ])

    const combined = []

    for (const d of deposits.data) {
      if (myAccountIds.includes(d.account_id)) {
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
      if (myAccountIds.includes(i.source_account_id)) {
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

    combined.sort((a, b) => new Date(b.date) - new Date(a.date))
    rows.value = combined
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

.tx-tile--in { background: #ECFDF5; color: var(--bank-credit); }
.tx-tile--out { background: #FEF2F2; color: var(--bank-debit); }
.tx-tile--count { background: #EFF6FF; color: #1D4ED8; }
</style>
