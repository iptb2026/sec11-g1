<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Account Types</div>
      <q-space />
      <q-btn color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :filter="search" :rows="rows" :columns="columns" row-key="id" :loading="loading" flat bordered>
      <template #top-right>
        <q-input v-model="search" dense clearable placeholder="Search">
          <template #append><q-icon name="search" /></template>
        </q-input>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense flat round icon="edit" color="primary" @click="openEdit(props.row)" />
          <q-btn dense flat round icon="delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-form @submit="save">
          <q-card-section>
            <div class="text-h6">{{ editingId ? 'Edit Account Type' : 'New Account Type' }}</div>
          </q-card-section>

          <q-card-section class="q-gutter-md">
            <q-input v-model="form.type_code" :rules="[required]" lazy-rules label="Type Code" filled />
            <q-input v-model="form.type_name" :rules="[required]" lazy-rules label="Type Name" filled />
            <q-input v-model.number="form.minimum_balance" :rules="[nonNegative]" lazy-rules label="Minimum Balance" type="number" filled />
            <q-input v-model.number="form.opening_deposit" :rules="[nonNegative]" lazy-rules label="Opening Deposit" type="number" filled />
            <q-input v-model.number="form.annual_interest_rate" :rules="[nonNegative]" lazy-rules label="Annual Interest Rate %" type="number" filled />
            <q-input v-model.number="form.daily_withdrawal_limit" :rules="[nonNegative]" lazy-rules label="Daily Withdrawal Limit" type="number" filled />
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
import api from '@/services/api'
import { errorMessage } from '@/utils/notify-error'
import { required, nonNegative } from '@/utils/validation'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'type_code', label: 'Code', field: 'type_code', align: 'left' },
  { name: 'type_name', label: 'Name', field: 'type_name', align: 'left' },
  { name: 'minimum_balance', label: 'Min Balance', field: 'minimum_balance', align: 'right' },
  { name: 'opening_deposit', label: 'Opening Deposit', field: 'opening_deposit', align: 'right' },
  { name: 'annual_interest_rate', label: 'Annual Rate %', field: 'annual_interest_rate', align: 'right' },
  { name: 'daily_withdrawal_limit', label: 'Daily Limit', field: 'daily_withdrawal_limit', align: 'right' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const search = ref('')
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const emptyForm = () => ({
  type_code: '',
  type_name: '',
  minimum_balance: 0,
  opening_deposit: 0,
  annual_interest_rate: 0,
  daily_withdrawal_limit: 0,
})
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/account-types/')
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
    type_code: row.type_code,
    type_name: row.type_name,
    minimum_balance: Number(row.minimum_balance),
    opening_deposit: Number(row.opening_deposit),
    annual_interest_rate: Number(row.annual_interest_rate),
    daily_withdrawal_limit: Number(row.daily_withdrawal_limit),
  }
  showDialog.value = true
}

async function save () {
  try {
    if (editingId.value) {
      await api.put(`/account-types/${editingId.value}`, form.value)
    } else {
      await api.post('/account-types/', form.value)
    }
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Account type saved' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete account type "${row.type_name}"?`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/account-types/${row.id}`)
      $q.notify({ type: 'positive', message: 'Account type deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, 'Delete failed') })
    }
  })
}

onMounted(loadRows)
</script>
