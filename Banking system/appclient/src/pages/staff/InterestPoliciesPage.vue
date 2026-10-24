<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Interest Policies</div>
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
            <div class="text-h6">{{ editingId ? 'Edit Interest Policy' : 'New Interest Policy' }}</div>
          </q-card-section>

          <q-card-section class="q-gutter-md">
            <q-select
              v-model="form.account_type_id" :rules="[required]" lazy-rules
              label="Account Type"
              filled
              emit-value
              map-options
              :options="accountTypeOptions"
            />
            <q-input v-model="form.policy_name" :rules="[required]" lazy-rules label="Policy Name" filled />
            <q-input v-model.number="form.annual_rate" :rules="[required, nonNegative]" lazy-rules label="Annual Rate %" type="number" filled />
            <q-select
              v-model="form.compounding_frequency"
              label="Compounding Frequency"
              filled
              :options="['DAILY', 'MONTHLY', 'QUARTERLY', 'YEARLY']"
            />
            <q-input v-model="form.effective_date" :rules="[isDate]" lazy-rules label="Effective Date" filled hint="YYYY-MM-DD" />
            <q-input v-model="form.expiration_date" :rules="[optionalDate]" lazy-rules label="Expiration Date" filled hint="YYYY-MM-DD (optional)" />
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
import { required, nonNegative, isDate, optionalDate } from '@/utils/validation'

const $q = useQuasar()
const canWrite = useCanWrite()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_type', label: 'Account Type', field: (row) => accountTypeNameById.value[row.account_type_id] || row.account_type_id, align: 'left' },
  { name: 'policy_name', label: 'Policy Name', field: 'policy_name', align: 'left' },
  { name: 'annual_rate', label: 'Annual Rate %', field: 'annual_rate', align: 'right' },
  { name: 'compounding_frequency', label: 'Compounding', field: 'compounding_frequency', align: 'left' },
  { name: 'effective_date', label: 'Effective', field: 'effective_date', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const search = ref('')
const accountTypeOptions = ref([])
const accountTypeNameById = ref({})
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  account_type_id: null,
  policy_name: '',
  annual_rate: 0,
  compounding_frequency: 'MONTHLY',
  effective_date: '',
  expiration_date: '',
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/interest-policies/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

async function loadOptions () {
  const { data } = await api.get('/account-types/')
  accountTypeOptions.value = data.map((t) => ({ label: `${t.type_code} - ${t.type_name}`, value: t.id }))
  accountTypeNameById.value = Object.fromEntries(data.map((t) => [t.id, t.type_name]))
}

function openCreate () {
  editingId.value = null
  form.value = emptyForm()
  showDialog.value = true
}

function openEdit (row) {
  editingId.value = row.id
  form.value = {
    account_type_id: row.account_type_id,
    policy_name: row.policy_name,
    annual_rate: Number(row.annual_rate),
    compounding_frequency: row.compounding_frequency,
    effective_date: row.effective_date,
    expiration_date: row.expiration_date,
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/interest-policies/${editingId.value}`, form.value)
    } else {
      await api.post('/interest-policies/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Interest policy saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete interest policy "${row.policy_name}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/interest-policies/${row.id}`)
      $q.notify({ type: 'positive', message: 'Interest policy deleted' })
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
