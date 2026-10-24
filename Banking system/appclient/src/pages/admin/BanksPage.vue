<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Banks</div>
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
      <q-card style="width: 420px">
        <q-form @submit="save">
          <q-card-section>
            <div class="text-h6">{{ editingId ? 'Edit Bank' : 'New Bank' }}</div>
          </q-card-section>

          <q-card-section class="q-gutter-md">
            <q-input v-model="form.bank_code" :rules="[required]" lazy-rules label="Bank Code" filled />
            <q-input v-model="form.swift_code" label="SWIFT Code" filled />
            <q-input v-model="form.bank_name" :rules="[required]" lazy-rules label="Bank Name" filled />
            <q-input v-model="form.short_name" label="Short Name" filled />
            <q-input v-model="form.contact_email" :rules="[optionalEmail]" lazy-rules label="Contact Email" filled />
            <q-select
              v-model="form.status"
              label="Status"
              filled
              :options="['ACTIVE', 'INACTIVE']"
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
import { required, optionalEmail } from '@/utils/validation'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'bank_code', label: 'Code', field: 'bank_code', align: 'left' },
  { name: 'bank_name', label: 'Name', field: 'bank_name', align: 'left' },
  { name: 'swift_code', label: 'SWIFT', field: 'swift_code', align: 'left' },
  { name: 'contact_email', label: 'Contact Email', field: 'contact_email', align: 'left' },
  { name: 'status', label: 'Status', field: 'status', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const search = ref('')
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  bank_code: '',
  swift_code: '',
  bank_name: '',
  short_name: '',
  contact_email: '',
  status: 'ACTIVE',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/banks/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
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
    bank_code: row.bank_code,
    swift_code: row.swift_code,
    bank_name: row.bank_name,
    short_name: row.short_name,
    contact_email: row.contact_email,
    status: row.status,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/banks/${editingId.value}`, form.value)
    } else {
      await api.post('/banks/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Bank saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete bank "${row.bank_name}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/banks/${row.id}`)
      $q.notify({ type: 'positive', message: 'Bank deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, 'Delete failed') })
    }
  })
}

onMounted(loadRows)
</script>
