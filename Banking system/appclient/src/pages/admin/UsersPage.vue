<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Users</div>
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
          <q-btn dense flat round icon="edit" aria-label="Edit" color="primary" @click="openEdit(props.row)" />
          <q-btn dense flat round icon="delete" aria-label="Delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 460px">
        <q-form @submit="save">
          <q-card-section>
            <div class="text-h6">{{ editingId ? 'Edit User' : 'New User' }}</div>
          </q-card-section>

          <q-card-section class="q-gutter-md">
            <q-input v-model="form.username" :rules="[required]" lazy-rules label="Username" filled />
            <q-input
              v-model="form.password" :rules="[required]" lazy-rules
              label="Password"
              type="password"
              filled
              :hint="editingId ? 'Required to save: re-enter the current password or set a new one' : 'Hashed by the backend'"
            />
            <q-input v-model="form.email" :rules="[optionalEmail]" lazy-rules label="Email" filled />
            <q-input v-model="form.mobile_number" label="Mobile Number" filled />
            <q-input v-model="form.first_name" :rules="[required]" lazy-rules label="First Name" filled />
            <q-input v-model="form.middle_name" label="Middle Name" filled />
            <q-input v-model="form.last_name" :rules="[required]" lazy-rules label="Last Name" filled />
            <q-input v-model="form.date_of_birth" :rules="[optionalDate]" lazy-rules label="Date of Birth" filled hint="YYYY-MM-DD" />
            <q-select
              v-model="form.role_id" :rules="[required]" lazy-rules
              label="Role"
              filled
              emit-value
              map-options
              :options="roleOptions"
            />
            <q-select
              v-model="form.account_status"
              label="Account Status"
              filled
              :options="['ACTIVE', 'LOCKED', 'DISABLED']"
            />
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
import { required, optionalDate, optionalEmail } from '@/utils/validation'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'username', label: 'Username', field: 'username', align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'first_name', label: 'First Name', field: 'first_name', align: 'left' },
  { name: 'last_name', label: 'Last Name', field: 'last_name', align: 'left' },
  { name: 'role_id', label: 'Role ID', field: 'role_id', align: 'left' },
  { name: 'account_status', label: 'Status', field: 'account_status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const search = ref('')
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

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/users/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

async function loadRoleOptions () {
  const { data } = await api.get('/roles/')
  roleOptions.value = data.map((r) => ({ label: `${r.role_code} - ${r.role_name}`, value: r.id }))
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
      await api.put(`/users/${editingId.value}`, form.value)
    } else {
      await api.post('/users/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'User saved' })
    loadRows()
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
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, 'Delete failed') })
    }
  })
}

onMounted(() => {
  loadRows()
  loadRoleOptions()
})
</script>
