<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-grey-9">Connected Banks</div>
      <q-btn
        color="primary"
        icon="add"
        label="NEW"
        no-caps
        unelevated
        class="text-weight-bold q-px-md"
        @click="openCreateDialog"
      />
    </div>

    <q-card flat bordered class="bg-white rounded-borders">
      <q-table
        :rows="items"
        :columns="columns"
        row-key="id"
        :loading="loading"
        :pagination="initialPagination"
        :rows-per-page-options="[5, 10, 20, 50]"
        flat
      >
        <template v-slot:body-cell-status="props">
          <q-td :props="props">
            <q-badge :color="props.row.status === 'ACTIVE' ? 'positive' : 'grey-6'" :label="props.row.status" />
          </q-td>
        </template>

        <template v-slot:body-cell-actions="props">
          <q-td :props="props" align="right">
            <q-btn flat round dense color="primary" icon="edit" class="q-mr-xs" @click="openEditDialog(props.row)">
              <q-tooltip>Edit</q-tooltip>
            </q-btn>
            <q-btn flat round dense color="negative" icon="delete" @click="confirmDelete(props.row)">
              <q-tooltip>Delete</q-tooltip>
            </q-btn>
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="min-width: 450px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-weight-bold">{{ isEditing ? 'Edit Bank' : 'New Bank' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-md">
          <q-form @submit="saveItem" class="q-gutter-md">
            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input v-model="form.bank_code" label="Bank Code *" outlined dense :disable="isEditing" :rules="[val => !!val || 'Required']" />
              </div>
              <div class="col-6">
                <q-input v-model="form.swift_code" label="SWIFT Code" outlined dense />
              </div>
            </div>

            <q-input v-model="form.bank_name" label="Bank Name *" outlined dense :rules="[val => !!val || 'Required']" />
            <q-input v-model="form.short_name" label="Short Name" outlined dense />
            <q-input v-model="form.api_endpoint" label="API Endpoint URL" outlined dense placeholder="https://..." />
            <q-input v-model="form.contact_email" label="Contact Email" outlined dense type="email" />

            <q-select
              v-model="form.status"
              :options="['ACTIVE', 'INACTIVE']"
              label="Status"
              outlined
              dense
            />

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
        <q-card-section class="text-grey-8">
          Delete bank <strong>{{ itemToDelete?.bank_name }}</strong>?
        </q-card-section>
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
import { api, defaultBanks } from '@/services/api'

const $q = useQuasar()
const items = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const dialogOpen = ref(false)
const isEditing = ref(false)
const deleteDialogOpen = ref(false)
const itemToDelete = ref(null)

const form = ref({
  id: null,
  bank_code: '',
  swift_code: '',
  bank_name: '',
  short_name: '',
  api_endpoint: '',
  contact_email: '',
  status: 'ACTIVE'
})

const initialPagination = { sortBy: 'id', descending: false, page: 1, rowsPerPage: 5 }

const columns = [
  { name: 'id', label: 'ID', align: 'left', field: 'id', sortable: true, style: 'width: 70px' },
  { name: 'bank_code', label: 'Code', align: 'left', field: 'bank_code', sortable: true },
  { name: 'bank_name', label: 'Bank Name', align: 'left', field: 'bank_name', sortable: true },
  { name: 'short_name', label: 'Short Name', align: 'left', field: 'short_name', sortable: true },
  { name: 'swift_code', label: 'SWIFT', align: 'left', field: 'swift_code' },
  { name: 'contact_email', label: 'Email', align: 'left', field: 'contact_email' },
  { name: 'status', label: 'Status', align: 'left', field: 'status', sortable: true },
  { name: 'actions', label: 'Actions', align: 'right', field: 'actions', style: 'width: 120px' }
]

async function loadItems() {
  loading.value = true
  try {
    const data = await api.banks.list()
    items.value = Array.isArray(data) && data.length > 0 ? data : defaultBanks
  } catch {
    items.value = defaultBanks
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  form.value = { id: null, bank_code: '', swift_code: '', bank_name: '', short_name: '', api_endpoint: '', contact_email: '', status: 'ACTIVE' }
  dialogOpen.value = true
}

function openEditDialog(item) {
  isEditing.value = true
  form.value = { ...item }
  dialogOpen.value = true
}

async function saveItem() {
  saving.value = true
  try {
    if (isEditing.value) {
      const updated = await api.banks.update(form.value.id, form.value).catch(() => ({ ...form.value }))
      const idx = items.value.findIndex(i => i.id === form.value.id)
      if (idx !== -1) items.value[idx] = { ...items.value[idx], ...updated }
      $q.notify({ type: 'positive', message: 'Bank updated', position: 'top' })
    } else {
      const created = await api.banks.create(form.value).catch(() => ({
        id: items.value.length > 0 ? Math.max(...items.value.map(i => i.id)) + 1 : 1,
        ...form.value,
        created_at: new Date().toISOString()
      }))
      items.value.push(created)
      $q.notify({ type: 'positive', message: 'Bank created', position: 'top' })
    }
    dialogOpen.value = false
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Save error', position: 'top' })
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
    await api.banks.delete(itemToDelete.value.id).catch(() => {})
    items.value = items.value.filter(i => i.id !== itemToDelete.value.id)
    $q.notify({ type: 'positive', message: 'Bank deleted', position: 'top' })
    deleteDialogOpen.value = false
  } finally {
    deleting.value = false
  }
}

onMounted(loadItems)
</script>

