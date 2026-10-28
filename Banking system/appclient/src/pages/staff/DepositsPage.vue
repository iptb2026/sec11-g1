<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Deposits</div>
      <q-space />
      <q-btn v-if="canWrite" color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :filter="search" :rows="rows" :columns="tableColumns(columns, canWrite)" row-key="id" :loading="loading" :pagination="{ rowsPerPage: 10 }" flat bordered>
      <template #top-right>
        <q-input v-model="search" dense clearable placeholder="Search">
          <template #append><q-icon name="search" /></template>
        </q-input>
      </template>
      <template #body-cell-status="props">
        <q-td :props="props">
          <q-badge :color="statusColor[props.row.status] || 'grey-7'">{{ statusLabel[props.row.status] || props.row.status }}</q-badge>
        </q-td>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <template v-if="isAdmin && props.row.status === 'PENDING'">
            <q-btn dense flat round icon="check_circle" aria-label="Approve" color="positive" @click="review(props.row, 'approve')">
              <q-tooltip>Approve: the money enters the account</q-tooltip>
            </q-btn>
            <q-btn dense flat round icon="cancel" aria-label="Reject" color="negative" @click="review(props.row, 'reject')">
              <q-tooltip>Reject: no money moves</q-tooltip>
            </q-btn>
          </template>
          <q-btn dense flat round icon="edit" aria-label="Edit" color="primary" @click="openEdit(props.row)" />
          <q-btn dense flat round icon="delete" aria-label="Delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-form @submit="save">
          <q-card-section>
            <div class="text-h6">{{ editingId ? 'Edit Deposit' : 'New Deposit' }}</div>
          </q-card-section>

          <q-card-section class="q-gutter-md">
            <q-select
              v-model="form.account_id" :rules="[required]" lazy-rules
              label="Account"
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
            <q-input
              v-if="form.account_id"
              :model-value="accountHolderName"
              label="Account Holder"
              filled
              readonly
            />
            <q-input v-model="form.reference_number" label="Reference Number" filled />
            <q-input v-model.number="form.amount" :rules="[positiveAmount]" lazy-rules label="Amount" type="number" filled
              :readonly="!!editingId"
              :hint="amountHint"
            />
            <q-select
              v-model="form.deposit_channel" :rules="[required]" lazy-rules
              label="Channel"
              filled
              use-input
              hide-selected
              fill-input
              input-debounce="0"
              :options="filteredChannelOptions"
              @filter="filterChannelOptions"
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
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { tableColumns } from '@/utils/tableColumns'
import api from '@/services/api'
import { useCanWrite } from '@/utils/permissions'
import { useAuthStore } from '@/stores/auth-store'
import { errorMessage } from '@/utils/notify-error'
import { required, positiveAmount } from '@/utils/validation'

const $q = useQuasar()
const canWrite = useCanWrite()
const isAdmin = useAuthStore().isAdmin

// Staff deposits of this amount or more wait for an admin (LARGE_DEPOSIT_THRESHOLD on the server).
const APPROVAL_THRESHOLD = 50000
const statusLabel = { PENDING: 'Pending approval', COMPLETED: 'Completed', REJECTED: 'Rejected' }
const statusColor = { PENDING: 'warning', COMPLETED: 'positive', REJECTED: 'negative' }

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_id', label: 'Auto ID', field: 'account_id', align: 'left' },
  { name: 'account_number', label: 'Account Number', field: (row) => accountNumberByAccountId.value[row.account_id] || '', align: 'left' },
  { name: 'account_name', label: 'Account Name', field: (row) => accountHolderByAccountId.value[row.account_id] || '', align: 'left' },
  { name: 'reference_number', label: 'Reference', field: 'reference_number', align: 'left' },
  { name: 'amount', label: 'Amount', field: 'amount', align: 'right' },
  { name: 'deposit_channel', label: 'Channel', field: 'deposit_channel', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left' },
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
const emptyForm = () => ({ account_id: null, reference_number: '', amount: null, deposit_channel: '', remarks: '' })
const form = ref(emptyForm())

const accountHolderName = computed(() => accountHolderByAccountId.value[form.value.account_id] || '')

const amountHint = computed(() => {
  if (editingId.value) return 'Account and amount cannot change. Delete it (which reverses it) and record a new one instead.'
  if (!isAdmin && form.value.amount >= APPROVAL_THRESHOLD) return `₱${APPROVAL_THRESHOLD.toLocaleString()} or more needs an admin's approval before it reaches the account.`
  return ''
})

const channelOptions = ['CASH', 'ONLINE', 'INTERBANK']
const filteredChannelOptions = ref(channelOptions)
function filterChannelOptions (val, update) {
  update(() => {
    if (val === '') {
      filteredChannelOptions.value = channelOptions
    } else {
      const needle = val.toLowerCase()
      filteredChannelOptions.value = channelOptions.filter((v) => v.toLowerCase().includes(needle))
    }
  })
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/deposits/')
    // Newest first: a higher id is a later deposit (the server sets the date).
    rows.value = [...data].sort((a, b) => b.id - a.id)
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
    account_id: row.account_id,
    reference_number: row.reference_number,
    amount: Number(row.amount),
    deposit_channel: row.deposit_channel,
    remarks: row.remarks,
  }
  showDialog.value = true
}

async function save () {
  try {
    let saved
    if (editingId.value) {
      ({ data: saved } = await api.put(`/deposits/${editingId.value}`, form.value))
    } else {
      ({ data: saved } = await api.post('/deposits/', form.value))
    }
    showDialog.value = false
    if (saved.status === 'PENDING') {
      $q.notify({ type: 'warning', message: `Deposit ${saved.reference_number} is waiting for an admin's approval` })
    } else {
      $q.notify({ type: 'positive', message: `Deposit ${saved.reference_number} saved` })
    }
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function review (row, action) {
  const approving = action === 'approve'
  $q.dialog({
    title: approving ? 'Approve Deposit' : 'Reject Deposit',
    message: approving
      ? `Approve ${row.reference_number} for ₱${Number(row.amount).toLocaleString()}? The money enters account ${accountNumberByAccountId.value[row.account_id] || ''}.`
      : `Reject ${row.reference_number}? No money moves, and the deposit stays on record as rejected.`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.post(`/deposits/${row.id}/${action}`)
      $q.notify({ type: 'positive', message: approving ? 'Deposit approved' : 'Deposit rejected' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, approving ? 'Approve failed' : 'Reject failed') })
    }
  })
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: row.status === 'COMPLETED'
      ? `Delete deposit "${row.reference_number}"? The amount leaves the account again.`
      : `Delete deposit "${row.reference_number}"? It never reached the account, so no money moves.`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/deposits/${row.id}`)
      $q.notify({ type: 'positive', message: 'Deposit deleted' })
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
