<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Interbank Transfers</div>
      <q-space />
      <q-btn v-if="canWrite" color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :filter="search" :rows="rows" :columns="tableColumns(columns, canWrite)" row-key="id" :loading="loading" :pagination="{ rowsPerPage: 10 }" flat bordered>
      <template #top-right>
        <q-input v-model="search" dense clearable placeholder="Search">
          <template #append><q-icon name="search" /></template>
        </q-input>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="props.row.status === 'PROCESSING'"
            dense flat round icon="check_circle" color="positive"
            title="Mark SUCCESS"
            aria-label="Mark transfer as successful"
            @click="markStatus(props.row, 'SUCCESS')"
          />
          <q-btn
            v-if="props.row.status === 'PROCESSING'"
            dense flat round icon="cancel" color="negative"
            title="Mark FAILED"
            aria-label="Mark transfer as failed"
            @click="markStatus(props.row, 'FAILED')"
          />
          <q-btn
            v-if="props.row.status === 'SUCCESS'"
            dense flat round icon="undo" color="warning"
            title="Mark REVERSED (refunds amount + fee)"
            aria-label="Mark transfer as reversed"
            @click="confirmReverse(props.row)"
          />
          <q-btn dense flat round icon="delete" aria-label="Delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 460px">
        <q-form @submit="save">
          <q-card-section>
            <div class="text-h6">New Interbank Transfer</div>
          </q-card-section>

          <q-card-section class="q-gutter-md">
            <q-select
              v-model="form.source_account_id" :rules="[required]" lazy-rules
              label="Source Account"
              filled
              emit-value
              map-options
              :options="accountOptions"
            />
            <q-select
              v-model="form.target_bank_id" :rules="[required]" lazy-rules
              label="Target Bank"
              filled
              emit-value
              map-options
              :options="bankOptions"
            />
            <q-input v-model="form.target_account_number" :rules="[required]" lazy-rules label="Target Account Number" filled />
            <q-input v-model="form.beneficiary_name" label="Beneficiary Name" filled />
            <q-input v-model="form.reference_number" label="Reference Number" filled />
            <q-input v-model.number="form.amount" :rules="[positiveAmount]" lazy-rules label="Amount" type="number" filled />
            <q-input v-model.number="form.transfer_fee" :rules="[nonNegative]" lazy-rules label="Transfer Fee" type="number" filled />
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
import { useCanWrite } from '@/utils/permissions'
import { errorMessage } from '@/utils/notify-error'
import { required, positiveAmount, nonNegative } from '@/utils/validation'

const $q = useQuasar()
const canWrite = useCanWrite()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'source_account_number', label: 'From Account', field: (row) => accountNumberByAccountId.value[row.source_account_id] || row.source_account_id, align: 'left' },
  { name: 'source_account_name', label: 'From Name', field: (row) => accountHolderByAccountId.value[row.source_account_id] || '', align: 'left' },
  { name: 'target_bank', label: 'To Bank', field: (row) => bankNameById.value[row.target_bank_id] || row.target_bank_id, align: 'left' },
  { name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'transfer_fee', label: 'Fee', field: 'transfer_fee', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const search = ref('')
const accountOptions = ref([])
const bankOptions = ref([])
const accountNumberByAccountId = ref({})
const accountHolderByAccountId = ref({})
const bankNameById = ref({})
const loading = ref(false)
const showDialog = ref(false)
const emptyForm = () => ({
  source_account_id: null,
  target_bank_id: null,
  target_account_number: '',
  beneficiary_name: '',
  reference_number: '',
  amount: null,
  transfer_fee: 0,
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/interbank-transfers/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

async function loadOptions () {
  const [{ data: accounts }, { data: users }, { data: banks }] = await Promise.all([
    api.get('/accounts/'),
    api.get('/users/'),
    api.get('/banks/'),
  ])

  const nameByUserId = {}
  users.forEach((u) => {
    nameByUserId[u.id] = `${u.first_name} ${u.last_name}`
  })

  accountOptions.value = accounts.map((a) => ({ label: a.account_number, value: a.id }))
  accountNumberByAccountId.value = Object.fromEntries(accounts.map((a) => [a.id, a.account_number]))
  accountHolderByAccountId.value = Object.fromEntries(
    accounts.map((a) => [a.id, nameByUserId[a.customer_id] || '']),
  )

  bankOptions.value = banks.map((b) => ({ label: `${b.bank_code} - ${b.bank_name}`, value: b.id }))
  bankNameById.value = Object.fromEntries(banks.map((b) => [b.id, b.bank_name]))
}

function openCreate () {
  form.value = emptyForm()
  showDialog.value = true
}

// A sent transfer can't be edited (the backend has no PUT for it); its
// status is changed with the buttons in the table instead.
async function save () {
  try {
    const { data } = await api.post('/interbank-transfers/', form.value)
    showDialog.value = false
    $q.notify({ type: 'positive', message: `Interbank transfer ${data.reference_number} saved` })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

async function markStatus (row, status) {
  try {
    await api.put(`/interbank-transfers/${row.id}/status`, { status })
    $q.notify({ type: 'positive', message: `Marked ${status}` })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Status update failed') })
  }
}

function confirmReverse (row) {
  $q.dialog({
    title: 'Reverse Transfer',
    message: `Mark "${row.reference_number}" as REVERSED? The amount and fee go back to the source account. This can't be undone.`,
    cancel: true,
    persistent: true,
  }).onOk(() => markStatus(row, 'REVERSED'))
}

function removeRow (row) {
  const refundNote = ['FAILED', 'REVERSED'].includes(row.status)
    ? ''
    : ' The amount and fee go back to the source account.'
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete interbank transfer "${row.reference_number}"?${refundNote}`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/interbank-transfers/${row.id}`)
      $q.notify({ type: 'positive', message: 'Interbank transfer deleted' })
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
