<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Accounts</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table
      :rows="groupedRows"
      :columns="tableColumns(columns)"
      :row-key="rowKey"
      :loading="loading"
      flat
      bordered
      :pagination="{ rowsPerPage: 0 }"
      :rows-per-page-options="[0]"
    >
      <template v-slot:body="props">
        <q-tr v-if="props.row.isGroupHeader" :key="props.row.key">
          <q-td colspan="100%" class="bg-grey-2 text-weight-bold">
            <q-icon name="person" class="q-mr-sm" />{{ props.row.groupLabel }}
          </q-td>
        </q-tr>
        <q-tr v-else :props="props">
          <q-td v-for="col in props.cols" :key="col.name" :props="props">
            <template v-if="col.name === 'actions'">
              <q-btn dense flat round icon="edit" aria-label="Edit" color="primary" @click="openEdit(props.row)" />
              <q-btn dense flat round icon="delete" aria-label="Delete" color="negative" @click="removeRow(props.row)" />
            </template>
            <template v-else>{{ col.value }}</template>
          </q-td>
        </q-tr>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 440px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit Account' : 'New Account' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <!-- The account number is assigned by the backend (1000000000 + id): a new account
               shows the number it will get, an existing one shows its number. Never typed in. -->
          <q-input
            :model-value="form.account_number"
            label="Account Number"
            filled
            readonly
            :loading="!editingId && !form.account_number"
            :hint="editingId ? '' : 'Assigned automatically'"
          >
            <template #prepend><q-icon name="tag" /></template>
          </q-input>
          <q-select
            v-model="form.customer_id"
            label="Customer"
            filled
            emit-value
            map-options
            :options="customerOptions"
          />
          <q-select
            v-model="form.account_type_id"
            label="Account Type"
            filled
            emit-value
            map-options
            :options="accountTypeOptions"
            :hint="selectedTypeHint"
          />
          <q-select
            v-if="editingId"
            v-model="form.status"
            label="Status"
            filled
            :options="['ACTIVE', 'FROZEN', 'CLOSED']"
          />
          <q-select v-model="form.currency_code" label="Currency" filled :options="['PHP', 'USD']" />
          <q-input v-model="form.branch_code" label="Branch Code" filled />
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
  { name: 'account_number', label: 'Account #', field: 'account_number', align: 'left' },
  { name: 'customer_id', label: 'Customer ID', field: 'customer_id', align: 'left' },
  { name: 'account_type_id', label: 'Type', field: (row) => accountTypeById.value[row.account_type_id]?.type_code || row.account_type_id, align: 'left' },
  { name: 'available_balance', label: 'Available Balance', field: 'available_balance', align: 'right' },
  { name: 'ledger_balance', label: 'Ledger Balance', field: 'ledger_balance', align: 'right' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const customerOptions = ref([])
const accountTypeOptions = ref([])
const customerNameById = ref({})
const accountTypeById = ref({})
const loading = ref(false)

function rowKey (row) {
  return row.isGroupHeader ? row.key : row.id
}

const groupedRows = computed(() => {
  const sorted = [...rows.value].sort((a, b) => {
    const nameA = customerNameById.value[a.customer_id] || ''
    const nameB = customerNameById.value[b.customer_id] || ''
    return nameA.localeCompare(nameB) || a.account_number.localeCompare(b.account_number)
  })

  const result = []
  let lastCustomerId = null
  for (const row of sorted) {
    if (row.customer_id !== lastCustomerId) {
      result.push({
        isGroupHeader: true,
        key: `group-${row.customer_id}`,
        groupLabel: customerNameById.value[row.customer_id] || `Customer #${row.customer_id}`,
      })
      lastCustomerId = row.customer_id
    }
    result.push(row)
  }
  return result
})
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  account_number: '',
  customer_id: null,
  account_type_id: null,
  currency_code: 'PHP',
  branch_code: '',
  status: 'ACTIVE',
})
const form = ref(emptyForm())

const selectedTypeHint = computed(() => {
  const t = accountTypeById.value[form.value.account_type_id]
  if (!t) return ''
  const limit = Number(t.daily_withdrawal_limit) ? t.daily_withdrawal_limit : 'none'
  return editingId.value
    ? `Min balance ${t.minimum_balance} · Daily limit ${limit}`
    : `Opens with ${t.opening_deposit} · Min balance ${t.minimum_balance} · Daily limit ${limit}`
})

async function loadRows ({ silent = false } = {}) {
  if (!silent) loading.value = true
  try {
    const { data } = await api.get('/accounts/')
    rows.value = data
  } catch (err) {
    if (!silent) $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

async function loadOptions () {
  const { data: users } = await api.get('/users/')
  const { data: roles } = await api.get('/roles/')
  const customerRoleIds = roles.filter((r) => r.role_code === 'CUSTOMER').map((r) => r.id)
  // Same rule as the backend: only ACTIVE users with the CUSTOMER role can own an account.
  customerOptions.value = users
    .filter((u) => customerRoleIds.includes(u.role_id) && u.account_status === 'ACTIVE')
    .map((u) => ({ label: `${u.username} (${u.first_name} ${u.last_name})`, value: u.id }))
  customerNameById.value = Object.fromEntries(users.map((u) => [u.id, `${u.first_name} ${u.last_name}`]))

  const { data: types } = await api.get('/account-types/')
  accountTypeOptions.value = types.map((t) => ({ label: `${t.type_code} - ${t.type_name}`, value: t.id }))
  accountTypeById.value = Object.fromEntries(types.map((t) => [t.id, t]))
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

async function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
  // Show the number this account will get; the backend assigns the final one on save.
  try {
    const { data } = await api.get('/accounts/next-number')
    if (!editingId.value) form.value.account_number = data.account_number
  } catch {
    form.value.account_number = 'Assigned on save'
  }
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_number: row.account_number,
    customer_id: row.customer_id,
    account_type_id: row.account_type_id,
    currency_code: row.currency_code,
    branch_code: row.branch_code,
    status: row.status,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/accounts/${editingId.value}`, form.value)
    } else {
      // status is always ACTIVE on opening — the backend sets it.
      const body = { ...form.value }
      delete body.status
      delete body.account_number // assigned by the backend
      const { data } = await api.post('/accounts/', body)
      showDialog.value = false
      $q.notify({ type: 'positive', message: `Account ${data.account_number} opened` })
      await refresh()
      return
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Account saved' })
    await refresh()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete account "${row.account_number}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/accounts/${row.id}`)
      $q.notify({ type: 'positive', message: 'Account deleted' })
      await refresh()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, 'Delete failed') })
    }
  })
}

useAutoRefresh(refresh)
</script>
