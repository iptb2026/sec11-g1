<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-grey-9">System Users</div>
      <q-btn color="primary" icon="add" label="NEW" no-caps unelevated class="text-weight-bold q-px-md" @click="openCreateDialog" />
    </div>

    <q-card flat bordered class="bg-white rounded-borders">
      <q-table :rows="items" :columns="columns" row-key="id" :loading="loading" :pagination="initialPagination" flat>
        <template v-slot:body-cell-status="props">
          <q-td :props="props">
            <q-badge :color="props.row.status === 'ACTIVE' ? 'positive' : 'grey-6'" :label="props.row.status || 'ACTIVE'" />
          </q-td>
        </template>
        <template v-slot:body-cell-actions="props">
          <q-td :props="props" align="right">
            <q-btn flat round dense color="primary" icon="edit" class="q-mr-xs" @click="openEditDialog(props.row)" />
            <q-btn flat round dense color="negative" icon="delete" @click="confirmDelete(props.row)" />
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="min-width: 450px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-weight-bold">{{ isEditing ? 'Edit User' : 'New User' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section class="q-pt-md">
          <q-form @submit="saveItem" class="q-gutter-md">
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input v-model="form.first_name" label="First Name *" outlined dense :rules="[val => !!val || 'Required']" />
              </div>
              <div class="col-6">
                <q-input v-model="form.last_name" label="Last Name *" outlined dense :rules="[val => !!val || 'Required']" />
              </div>
            </div>
            <q-input v-model="form.username" label="Username *" outlined dense :disable="isEditing" :rules="[val => !!val || 'Required']" />
            <q-input v-model="form.email" label="Email Address *" outlined dense type="email" :rules="[val => !!val || 'Required']" />
            <q-input v-if="!isEditing" v-model="form.password" label="Password *" outlined dense type="password" :rules="[val => !!val || 'Required']" />
            <q-select v-model="form.role_id" :options="roleOptions" emit-value map-options label="Role *" outlined dense :rules="[val => !!val || 'Required']" />
            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn label="Cancel" flat color="grey-7" v-close-popup />
              <q-btn :label="isEditing ? 'Update' : 'Create'" type="submit" color="primary" unelevated :loading="saving" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <q-dialog v-model="deleteDialogOpen">
      <q-card style="min-width: 350px;">
        <q-card-section class="text-h6 text-weight-bold text-negative">Confirm Deletion</q-card-section>
        <q-card-section class="text-grey-8">Delete user <strong>{{ itemToDelete?.username }}</strong>?</q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="grey-7" v-close-popup />
          <q-btn unelevated label="Delete" color="negative" :loading="deleting" @click="executeDelete" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api, defaultUsers } from '@/services/api'

const $q = useQuasar()
const items = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const dialogOpen = ref(false)
const isEditing = ref(false)
const deleteDialogOpen = ref(false)
const itemToDelete = ref(null)

const roleOptions = [
  { label: 'Admin', value: 1 },
  { label: 'Staff', value: 2 },
  { label: 'Customer', value: 3 },
  { label: 'Auditor', value: 4 }
]

const form = ref({ id: null, username: '', email: '', first_name: '', last_name: '', password: '', role_id: 3, status: 'ACTIVE' })
const initialPagination = { sortBy: 'id', descending: false, page: 1, rowsPerPage: 5 }

const columns = [
  { name: 'id', label: 'ID', align: 'left', field: 'id', sortable: true, style: 'width: 70px' },
  { name: 'username', label: 'Username', align: 'left', field: 'username', sortable: true },
  { name: 'name', label: 'Full Name', align: 'left', field: row => `${row.first_name || ''} ${row.last_name || ''}`.trim(), sortable: true },
  { name: 'email', label: 'Email', align: 'left', field: 'email', sortable: true },
  { name: 'role_name', label: 'Role', align: 'left', field: row => row.role_name || (roleOptions.find(r => r.value === row.role_id)?.label || 'Customer'), sortable: true },
  { name: 'status', label: 'Status', align: 'left', field: 'status', sortable: true },
  { name: 'actions', label: 'Actions', align: 'right', field: 'actions', style: 'width: 120px' }
]

async function loadItems() {
  loading.value = true
  try {
    const data = await api.users.list()
    items.value = Array.isArray(data) && data.length > 0 ? data : defaultUsers
  } catch {
    items.value = defaultUsers
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  form.value = { id: null, username: '', email: '', first_name: '', last_name: '', password: '', role_id: 3, status: 'ACTIVE' }
  dialogOpen.value = true
}

function openEditDialog(item) {
  isEditing.value = true
  form.value = { ...item, password: '' }
  dialogOpen.value = true
}

async function saveItem() {
  saving.value = true
  try {
    if (isEditing.value) {
      const updated = await api.users.update(form.value.id, form.value).catch(() => ({ ...form.value }))
      const idx = items.value.findIndex(i => i.id === form.value.id)
      if (idx !== -1) items.value[idx] = { ...items.value[idx], ...updated }
      $q.notify({ type: 'positive', message: 'User updated', position: 'top' })
    } else {
      const created = await api.users.create(form.value).catch(() => ({
        id: items.value.length > 0 ? Math.max(...items.value.map(i => i.id)) + 1 : 1,
        ...form.value
      }))
      items.value.push(created)
      $q.notify({ type: 'positive', message: 'User created', position: 'top' })
    }
    dialogOpen.value = false
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Error', position: 'top' })
  } finally {
    saving.value = false
  }
}

function confirmDelete(item) {
  itemToDelete.value = item
  deleteDialogOpen.value = true
}

async function executeDelete() {
  if (!itemToDelete.value) return
  deleting.value = true
  try {
    await api.users.delete(itemToDelete.value.id).catch(() => {})
    items.value = items.value.filter(i => i.id !== itemToDelete.value.id)
    $q.notify({ type: 'positive', message: 'User deleted', position: 'top' })
    deleteDialogOpen.value = false
  } finally {
    deleting.value = false
  }
}

onMounted(loadItems)
</script>

