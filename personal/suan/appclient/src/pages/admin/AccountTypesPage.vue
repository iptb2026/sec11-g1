<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Account Types</div>
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
      <q-card style="width: 420px">
        <q-card-section>
          <div class="text-h6">{{ editingId ? 'Edit Account Type' : 'New Account Type' }}</div>
        </q-card-section>

        <q-card-section class="q-gutter-md">
          <q-input v-model="form.type_code" label="Type Code" filled />
          <q-input v-model="form.type_name" label="Type Name" filled />
          <q-input v-model.number="form.minimum_balance" label="Minimum Balance" type="number" filled hint="Withdrawals and transfers cannot go below this" />
          <q-input v-model.number="form.opening_deposit" label="Opening Deposit" type="number" filled hint="Starting balance of new accounts; must be at least the minimum balance" />
          <q-input v-model.number="form.annual_interest_rate" label="Annual Interest Rate %" type="number" filled />
          <q-input v-model.number="form.daily_withdrawal_limit" label="Daily Withdrawal Limit" type="number" filled hint="Copied to each new account's withdrawal limit; 0 = no limit" />
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
import api, { errorMessage } from '@/services/api'

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

async function loadRows ({ silent = false } = {}) {
  if (!silent) loading.value = true
  try {
    const { data } = await api.get('/account-types/')
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
    await refresh()
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
      await refresh()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, 'Delete failed') })
    }
  })
}

useAutoRefresh(refresh)
</script>
