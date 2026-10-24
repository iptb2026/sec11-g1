<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Ledger Entries</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :filter="search" :rows="rows" :columns="tableColumns(columns)" row-key="id" :loading="loading" flat bordered>
      <template #top-right>
        <q-input v-model="search" dense clearable placeholder="Search">
          <template #append><q-icon name="search" /></template>
        </q-input>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense flat round icon="delete" aria-label="Delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <!-- balance_after is a point-in-time snapshot the backend fills in automatically -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-form @submit="save">
          <q-card-section>
            <div class="text-h6">New Ledger Entry</div>
          </q-card-section>

          <q-card-section class="q-gutter-md">
            <q-select
              v-model="form.account_id" :rules="[required]" lazy-rules
              label="Account"
              filled
              emit-value
              map-options
              :options="accountOptions"
            />
            <q-input v-model="form.transaction_reference" :rules="[required]" lazy-rules label="Transaction Reference" filled />
            <q-select
              v-model="form.transaction_type" :rules="[required]" lazy-rules
              label="Transaction Type"
              filled
              :options="transactionTypeOptions"
            />
            <q-input v-model.number="form.debit_amount" :rules="[nonNegative]" lazy-rules label="Debit Amount" type="number" filled />
            <q-input v-model.number="form.credit_amount" :rules="[nonNegative]" lazy-rules label="Credit Amount" type="number" filled />
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn color="primary" label="Save" type="submit" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { tableColumns } from '@/utils/tableColumns'
import api from '@/services/api'
import { errorMessage } from '@/utils/notify-error'
import { required, nonNegative } from '@/utils/validation'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_id', label: 'Account ID', field: 'account_id', align: 'left' },
  { name: 'transaction_reference', label: 'Reference', field: 'transaction_reference', align: 'left' },
  { name: 'transaction_type', label: 'Type', field: 'transaction_type', align: 'left' },
  { name: 'debit_amount', label: 'Debit', field: 'debit_amount', align: 'right' },
  { name: 'credit_amount', label: 'Credit', field: 'credit_amount', align: 'right' },
  { name: 'balance_after', label: 'Balance After', field: 'balance_after', align: 'right' },
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const search = ref('')
const accountOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const emptyForm = () => ({ account_id: null, transaction_reference: '', transaction_type: '', debit_amount: 0, credit_amount: 0 })

const transactionTypeOptions = [
  'DEPOSIT', 'WITHDRAWAL', 'TRANSFER_DEBIT', 'TRANSFER_CREDIT',
  'FEE', 'INTEREST', 'INTERBANK_DEBIT', 'INTERBANK_CREDIT', 'REVERSAL',
]
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/ledger-entries/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

async function loadOptions () {
  const { data } = await api.get('/accounts/')
  accountOptions.value = data.map((a) => ({ label: a.account_number, value: a.id }))
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
    loadRows()
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
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, 'Delete failed') })
    }
  })
}

onMounted(() => {
  loadRows()
  loadOptions()
})
</script>
