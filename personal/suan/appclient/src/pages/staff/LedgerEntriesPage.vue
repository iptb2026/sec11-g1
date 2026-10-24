<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Ledger Entries</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :rows="rows" :columns="tableColumns(columns)" row-key="id" :loading="loading" flat bordered>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense flat round icon="delete" aria-label="Delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <!-- balance_after is a point-in-time snapshot the backend fills in automatically -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-card-section>
          <div class="text-h6">New Ledger Entry</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-select
            v-model="form.account_id"
            label="Account"
            filled
            emit-value
            map-options
            :options="accountOptions"
          >
            <template v-slot:option="scope">
              <q-item v-bind="scope.itemProps">
                <q-item-section>
                  <q-item-label>{{ scope.opt.label }}</q-item-label>
                  <q-item-label caption>{{ scope.opt.holder }}</q-item-label>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
          <q-input
            v-if="form.account_id"
            :model-value="accountHolderName"
            label="Account Holder"
            filled
            readonly
          />
          <q-input v-model="form.transaction_reference" label="Transaction Reference" filled />
          <q-select v-model="form.transaction_type" label="Transaction Type" filled :options="transactionTypeOptions" />
          <q-input v-model.number="form.debit_amount" label="Debit Amount" type="number" filled />
          <q-input v-model.number="form.credit_amount" label="Credit Amount" type="number" filled />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn color="primary" label="Save" @click="save" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useAutoRefresh } from '@/composables/useAutoRefresh'
import { tableColumns } from '@/utils/tableColumns'
import api, { errorMessage } from '@/services/api'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_id', label: 'Account ID', field: 'account_id', align: 'left' },
  { name: 'account_number', label: 'Account Number', field: (row) => accountNumberByAccountId.value[row.account_id] || '', align: 'left' },
  { name: 'account_name', label: 'Account Name', field: (row) => accountHolderByAccountId.value[row.account_id] || '', align: 'left' },
  { name: 'transaction_reference', label: 'Reference', field: 'transaction_reference', align: 'left' },
  { name: 'transaction_type', label: 'Type', field: 'transaction_type', align: 'left' },
  { name: 'debit_amount', label: 'Debit', field: 'debit_amount', align: 'right' },
  { name: 'credit_amount', label: 'Credit', field: 'credit_amount', align: 'right' },
  { name: 'balance_after', label: 'Balance After', field: 'balance_after', align: 'right' },
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const accountOptions = ref([])
const accountNumberByAccountId = ref({})
const accountHolderByAccountId = ref({})
const accountHolderName = computed(() => accountHolderByAccountId.value[form.value.account_id] || '')

// Must match the backend's allowed values exactly, or the save fails with 422.
const transactionTypeOptions = [
  'DEPOSIT', 'WITHDRAWAL', 'TRANSFER_DEBIT', 'TRANSFER_CREDIT',
  'FEE', 'INTEREST', 'INTERBANK_DEBIT', 'INTERBANK_CREDIT', 'REVERSAL',
]
const loading = ref(false)
const showDialog = ref(false)
const emptyForm = () => ({ account_id: null, transaction_reference: '', transaction_type: '', debit_amount: 0, credit_amount: 0 })
const form = ref(emptyForm())

async function loadRows ({ silent = false } = {}) {
  if (!silent) loading.value = true
  try {
    const { data } = await api.get('/ledger-entries/')
    rows.value = data
  } catch (err) {
    if (!silent) $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

async function loadOptions () {
  const [{ data: accounts }, { data: users }] = await Promise.all([
    api.get('/accounts/'),
    api.get('/users/'),
  ])

  const nameByUserId = {}
  users.forEach((u) => {
    nameByUserId[u.id] = `${u.first_name} ${u.last_name}`
  })

  accountOptions.value = accounts.map((a) => ({
    label: a.account_number,
    value: a.id,
    holder: nameByUserId[a.customer_id] || '',
  }))
  accountNumberByAccountId.value = Object.fromEntries(accounts.map((a) => [a.id, a.account_number]))
  accountHolderByAccountId.value = Object.fromEntries(
    accounts.map((a) => [a.id, nameByUserId[a.customer_id] || '']),
  )
}

// Reloads the table AND the dropdown options, so balances, names, and
// newly added records show up right after any add / edit / delete.
// Also called in the background by useAutoRefresh (silent: no spinner/toasts).
async function refresh ({ silent = false } = {}) {
  try {
    await Promise.all([loadRows({ silent }), loadOptions()])
  } catch (err) {
    if (!silent) $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  }
}

function openCreate () {
  form.value = emptyForm()
  showDialog.value = true
}

async function save () {
  try {
    await api.post('/ledger-entries/', form.value)
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Ledger entry created' })
    await refresh()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete ledger entry #${row.id}?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/ledger-entries/${row.id}`)
      $q.notify({ type: 'positive', message: 'Ledger entry deleted' })
      await refresh()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, 'Delete failed') })
    }
  })
}

useAutoRefresh(refresh)
</script>
