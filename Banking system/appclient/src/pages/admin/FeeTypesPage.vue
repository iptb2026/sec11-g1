<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Fee Types</div>
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
            <div class="text-h6">{{ editingId ? 'Edit Fee Type' : 'New Fee Type' }}</div>
          </q-card-section>

          <q-card-section class="q-gutter-md">
            <q-input v-model="form.fee_code" :rules="[required]" lazy-rules label="Fee Code" filled />
            <q-input v-model="form.fee_name" :rules="[required]" lazy-rules label="Fee Name" filled />
            <q-input v-model="form.fee_description" label="Description" type="textarea" filled />
            <q-input v-model.number="form.fixed_amount" :rules="[nonNegative]" lazy-rules label="Fixed Amount" type="number" filled />
            <q-input v-model.number="form.percentage_rate" :rules="[nonNegative]" lazy-rules label="Percentage Rate %" type="number" filled />
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
import { required, nonNegative } from '@/utils/validation'

const $q = useQuasar()
const canWrite = useCanWrite()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'fee_code', label: 'Code', field: 'fee_code', align: 'left' },
  { name: 'fee_name', label: 'Name', field: 'fee_name', align: 'left' },
  { name: 'fixed_amount', label: 'Fixed Amount', field: 'fixed_amount', align: 'right' },
  { name: 'percentage_rate', label: 'Percentage %', field: 'percentage_rate', align: 'right' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const search = ref('')
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({ fee_code: '', fee_name: '', fee_description: '', fixed_amount: 0, percentage_rate: 0 })
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/fee-types/')
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
    fee_code: row.fee_code,
    fee_name: row.fee_name,
    fee_description: row.fee_description,
    fixed_amount: Number(row.fixed_amount),
    percentage_rate: Number(row.percentage_rate),
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/fee-types/${editingId.value}`, form.value)
    } else {
      await api.post('/fee-types/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Fee type saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete fee type "${row.fee_name}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/fee-types/${row.id}`)
      $q.notify({ type: 'positive', message: 'Fee type deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, 'Delete failed') })
    }
  })
}

onMounted(loadRows)
</script>
