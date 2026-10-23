<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Roles</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense flat round icon="edit" color="primary" @click="openEdit(props.row)" />
          <q-btn dense flat round icon="delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 400px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit Role' : 'New Role' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="form.role_code" label="Role Code" filled />
          <q-input v-model="form.role_name" label="Role Name" filled />
          <q-input v-model="form.description" label="Description" type="textarea" filled />
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
import api, { errorMessage } from '@/services/api'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'role_code', label: 'Code', field: 'role_code', align: 'left' },
  { name: 'role_name', label: 'Name', field: 'role_name', align: 'left' },
  { name: 'description', label: 'Description', field: 'description', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const form = ref({ role_code: '', role_name: '', description: '' })

async function loadRows ({ silent = false } = {}) {
  if (!silent) loading.value = true
  try {
    const { data } = await api.get('/roles/')
    rows.value = data
  } catch (err) {
    if (!silent) $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

// Reloads the table AND the dropdown options, so balances, names, and
// newly added records show up right after any add / edit / delete.
// Also called in the background by useAutoRefresh (silent: no spinner/toasts).
async function refresh ({ silent = false } = {}) {
  try {
    await Promise.all([loadRows({ silent })])
  } catch (err) {
    if (!silent) $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  }
}

function openCreate () {
  editingId.value = null
  form.value = { role_code: '', role_name: '', description: '' }
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = { role_code: row.role_code, role_name: row.role_name, description: row.description }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/roles/${editingId.value}`, form.value)
    } else {
      await api.post('/roles/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Role saved' })
    await refresh()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete role "${row.role_name}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/roles/${row.id}`)
      $q.notify({ type: 'positive', message: 'Role deleted' })
      await refresh()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, 'Delete failed') })
    }
  })
}

useAutoRefresh(refresh)
</script>
