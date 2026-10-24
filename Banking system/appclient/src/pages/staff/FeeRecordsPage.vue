<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Fee Records</div>
      <q-space />
      <q-btn v-if="canWrite" color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :filter="search" :rows="rows" :columns="tableColumns(columns, canWrite)" row-key="id" :loading="loading" flat bordered>
      <template #top-right>
        <q-input v-model="search" dense clearable placeholder="Search">
          <template #append><q-icon name="search" /></template>
        </q-input>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense flat round icon="edit" aria-label="Edit" color="primary" @click="openEdit(props.row)" />
          <q-btn dense flat round icon="delete" aria-label="Delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-form @submit="save">
          <q-card-section>
            <div class="text-h6">{{ editingId ? 'Edit Fee Record' : 'New Fee Record' }}</div>
          </q-card-section>

          <q-card-section class="q-gutter-md">
            <!-- Only remarks can change after a fee is charged (the backend refuses the rest). -->
            <q-select
              v-model="form.account_id" :rules="[required]" lazy-rules
              label="Account"
              filled
              emit-value
              map-options
              :options="accountOptions"
              :readonly="!!editingId"
            />
            <q-select
              v-model="form.fee_type_id" :rules="[required]" lazy-rules
              label="Fee Type"
              filled
              emit-value
              map-options
              :options="feeTypeOptions"
              :readonly="!!editingId"
            />
            <q-input
              v-model="form.transaction_reference"
              label="Transaction Reference"
              filled
              :readonly="!!editingId"
              hint="Reference of the deposit/withdrawal/transfer the fee is for"
            />
            <q-input
              v-if="editingId"
              :model-value="form.amount_charged"
              label="Amount Charged"
              filled
              readonly
            />
            <div v-else class="text-caption text-grey-7">
              The amount is calculated by the server from the fee type.
            </div>
            <q-input v-model="form.remarks" label="Remarks" type="textarea" filled />
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
import { required } from '@/utils/validation'

const $q = useQuasar()
const canWrite = useCanWrite()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_id', label: 'Account ID', field: 'account_id', align: 'left' },
  { name: 'fee_type_id', label: 'Fee Type ID', field: 'fee_type_id', align: 'left' },
  { name: 'transaction_reference', label: 'Reference', field: 'transaction_reference', align: 'left' },
  { name: 'amount_charged', label: 'Amount Charged', field: 'amount_charged', align: 'right' },
  { name: 'charged_at', label: 'Charged At', field: 'charged_at', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const search = ref('')
const accountOptions = ref([])
const feeTypeOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  account_id: null,
  fee_type_id: null,
  transaction_reference: '',
  remarks: '',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/fee-records/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

async function loadOptions () {
  const { data: accounts } = await api.get('/accounts/')
  accountOptions.value = accounts.map((a) => ({ label: a.account_number, value: a.id }))

  const { data: feeTypes } = await api.get('/fee-types/')
  feeTypeOptions.value = feeTypes.map((f) => ({ label: `${f.fee_code} - ${f.fee_name}`, value: f.id }))
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_id: row.account_id,
    fee_type_id: row.fee_type_id,
    transaction_reference: row.transaction_reference,
    amount_charged: row.amount_charged,
    remarks: row.remarks,
  }
  showDialog.value = true
}

async function save () {
  // amount_charged is only shown, never sent: the server calculates it.
  const { amount_charged, ...payload } = form.value
  try {
    if (editingId.value) {
      await api.put(`/fee-records/${editingId.value}`, payload)
    } else {
      await api.post('/fee-records/', payload)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Fee record saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete fee record #${row.id}? The fee is refunded to the account.`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/fee-records/${row.id}`)
      $q.notify({ type: 'positive', message: 'Fee record deleted' })
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
