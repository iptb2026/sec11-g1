<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Users</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :rows="rows" :columns="tableColumns(columns)" row-key="id" :loading="loading" flat bordered>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense flat round icon="edit" aria-label="Edit" color="primary" @click="openEdit(props.row)" />
          <q-btn dense flat round icon="delete" aria-label="Delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 460px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit User' : 'New User' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="form.username" label="Username" filled />
          <q-input v-model="form.password" label="Password" filled :hint="editingId ? 'Leave blank to keep the current password' : 'Plain text here, hashed by the backend'" />
          <q-input v-model="form.email" label="Email" filled />
          <q-input v-model="form.mobile_number" label="Mobile Number" filled />
          <q-input v-model="form.first_name" label="First Name" filled />
          <q-input v-model="form.middle_name" label="Middle Name" filled />
          <q-input v-model="form.last_name" label="Last Name" filled />
          <q-input v-model="form.date_of_birth" label="Date of Birth" type="date" stack-label filled />
          <q-select
            v-model="form.role_id"
            label="Role"
            filled
            emit-value
            map-options
            :options="roleOptions"
          />
          <q-select v-model="form.account_status" label="Account Status" filled :options="['ACTIVE', 'LOCKED', 'DISABLED']" />
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
import { ref } from 'vue'
import { useQuasar } from 'quasar'
import { useAutoRefresh } from '@/composables/useAutoRefresh'
import { tableColumns } from '@/utils/tableColumns'
import api, { errorMessage, blankToNull } from '@/services/api'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'username', label: 'Username', field: 'username', align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'first_name', label: 'First Name', field: 'first_name', align: 'left' },
  { name: 'last_name', label: 'Last Name', field: 'last_name', align: 'left' },
  { name: 'role_id', label: 'Role', field: (row) => roleOptions.value.find((o) => o.value === row.role_id)?.label || row.role_id, align: 'left' },
  { name: 'account_status', label: 'Status', field: 'account_status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const roleOptions = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  username: '',
  password: '',
  email: '',
  mobile_number: '',
  first_name: '',
  middle_name: '',
  last_name: '',
  date_of_birth: '',
  role_id: null,
  account_status: 'ACTIVE',
})
const form = ref(emptyForm())

async function loadRows ({ silent = false } = {}) {
  if (!silent) loading.value = true
  try {
    const { data } = await api.get('/users/')
    rows.value = data
  } catch (err) {
    if (!silent) $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

async function loadRoleOptions () {
  const { data } = await api.get('/roles/')
  roleOptions.value = data.map((r) => ({ label: `${r.role_code} - ${r.role_name}`, value: r.id }))
}

// Reloads the table AND the dropdown options, so balances, names, and
// newly added records show up right after any add / edit / delete.
// Also called in the background by useAutoRefresh (silent: no spinner/toasts).
async function refresh ({ silent = false } = {}) {
  try {
    await Promise.all([loadRows({ silent }), loadRoleOptions()])
  } catch (err) {
    if (!silent) $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  }
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    username: row.username,
    password: '',
    email: row.email,
    mobile_number: row.mobile_number,
    first_name: row.first_name,
    middle_name: row.middle_name,
    last_name: row.last_name,
    date_of_birth: row.date_of_birth,
    role_id: row.role_id,
    account_status: row.account_status,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/users/${editingId.value}`, blankToNull(form.value))
    } else {
      await api.post('/users/', blankToNull(form.value))
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'User saved' })
    await refresh()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete user "${row.username}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/users/${row.id}`)
      $q.notify({ type: 'positive', message: 'User deleted' })
      await refresh()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, 'Delete failed') })
    }
  })
}

useAutoRefresh(refresh)
</script>
