<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Transfers</div>
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
          <q-btn dense flat round icon="edit" aria-label="Edit" color="primary" @click="openEdit(props.row)" />
          <q-btn dense flat round icon="delete" aria-label="Delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 440px">
        <q-form @submit="save">
          <q-card-section>
            <div class="text-h6">{{ editingId ? 'Edit Transfer' : 'New Transfer' }}</div>
          </q-card-section>

          <q-card-section class="q-gutter-md">
            <q-select
              v-model="form.source_account_id" :rules="[required]" lazy-rules
              label="Source Account"
              filled
              emit-value
              map-options
              :options="accountOptions"
              :readonly="!!editingId"
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
            <q-select
              v-model="form.destination_account_id" :rules="[required, (val) => val !== form.source_account_id || 'Must be different from the source account']" lazy-rules
              label="Destination Account"
              filled
              emit-value
              map-options
              :options="accountOptions"
              :readonly="!!editingId"
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
            <q-input v-model="form.transfer_reference" :rules="[required]" lazy-rules label="Transfer Reference" filled />
            <q-input v-model.number="form.amount" :rules="[positiveAmount]" lazy-rules label="Amount" type="number" filled
              :readonly="!!editingId"
              :hint="editingId ? 'Account and amount cannot change. Delete it (which reverses it) and record a new one instead.' : ''"
            />
            <q-select
              v-model="form.transfer_type"
              label="Transfer Type"
              filled
              :options="['INTERNAL', 'SCHEDULED']"
            />
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
import { required, positiveAmount } from '@/utils/validation'
import { newReference } from '@/utils/reference'

const $q = useQuasar()
const canWrite = useCanWrite()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'from_account_number', label: 'From Account', field: (row) => accountNumberByAccountId.value[row.source_account_id] || row.source_account_id, align: 'left' },
  { name: 'from_account_name', label: 'From Name', field: (row) => accountHolderByAccountId.value[row.source_account_id] || '', align: 'left' },
  { name: 'to_account_number', label: 'To Account', field: (row) => accountNumberByAccountId.value[row.destination_account_id] || row.destination_account_id, align: 'left' },
  { name: 'to_account_name', label: 'To Name', field: (row) => accountHolderByAccountId.value[row.destination_account_id] || '', align: 'left' },
  { name: 'transfer_reference', label: 'Reference', field: 'transfer_reference', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const search = ref('')
const accountOptions = ref([])
const accountNumberByAccountId = ref({})
const accountHolderByAccountId = ref({})
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  source_account_id: null,
  destination_account_id: null,
  transfer_reference: newReference('TRF'),
  amount: null,
  transfer_type: 'INTERNAL',
  remarks: '',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/transfers/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
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

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    source_account_id: row.source_account_id,
    destination_account_id: row.destination_account_id,
    transfer_reference: row.transfer_reference,
    amount: Number(row.amount),
    transfer_type: row.transfer_type,
    remarks: row.remarks,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/transfers/${editingId.value}`, form.value)
    } else {
      await api.post('/transfers/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Transfer saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete transfer "${row.transfer_reference}"? The amount moves back to the source account.`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/transfers/${row.id}`)
      $q.notify({ type: 'positive', message: 'Transfer deleted' })
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
