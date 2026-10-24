<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-grey-9">Customer Accounts</div>
      <q-btn color="primary" icon="add" label="NEW" no-caps unelevated class="text-weight-bold q-px-md" @click="openCreateDialog" />
    </div>

    <q-card flat bordered class="bg-white rounded-borders">
      <q-table :rows="items" :columns="columns" row-key="id" :loading="loading" :pagination="initialPagination" flat>
        <template v-slot:body-cell-balance="props">
          <q-td :props="props" class="text-weight-bold text-primary">
            ₱{{ Number(props.row.available_balance ?? props.row.balance ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
          </q-td>
        </template>
        <template v-slot:body-cell-status="props">
          <q-td :props="props">
            <q-badge :color="props.row.status === 'ACTIVE' ? 'positive' : 'negative'" :label="props.row.status" />
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
          <div class="text-h6 text-weight-bold">{{ isEditing ? 'Edit Account' : 'Open New Account' }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section class="q-pt-md">
          <q-form @submit="saveItem" class="q-gutter-md">
            <q-input v-model="form.account_number" label="Account Number *" outlined dense :disable="isEditing" :rules="[val => !!val || 'Required']" />
            <q-input v-model="form.customer_id" label="Customer / User ID *" outlined dense type="number" :rules="[val => !!val || 'Required']" />
            <q-select v-model="form.account_type_id" :options="accountTypeOptions" emit-value map-options label="Account Type *" outlined dense :rules="[val => !!val || 'Required']" />
            <q-select v-if="isEditing" v-model="form.status" :options="['ACTIVE', 'FROZEN', 'CLOSED']" label="Status" outlined dense />
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
        <q-card-section class="text-grey-8">Delete account <strong>{{ itemToDelete?.account_number }}</strong>?</q-card-section>
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
import { api } from '@/services/api'

const $q = useQuasar()
const items = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const dialogOpen = ref(false)
const isEditing = ref(false)
const deleteDialogOpen = ref(false)
const itemToDelete = ref(null)

const accountTypeOptions = ref([
  { label: 'Savings Account', value: 1 },
  { label: 'Checking Account', value: 2 },
  { label: 'Time Deposit', value: 3 }
])

const form = ref({ id: null, account_number: '', customer_id: 1, account_type_id: 1, status: 'ACTIVE' })
const initialPagination = { sortBy: 'id', descending: false, page: 1, rowsPerPage: 5 }

const columns = [
  { name: 'id', label: 'ID', align: 'left', field: 'id', sortable: true, style: 'width: 70px' },
  { name: 'account_number', label: 'Account Number', align: 'left', field: 'account_number', sortable: true },
  { name: 'customer_id', label: 'Customer ID', align: 'left', field: row => row.customer_id ?? row.user_id, sortable: true },
  { name: 'account_type', label: 'Type', align: 'left', field: row => row.account_type || (accountTypeOptions.value.find(t => t.value === row.account_type_id)?.label || `Type #${row.account_type_id}`) },
  { name: 'balance', label: 'Balance', align: 'left', field: row => row.available_balance ?? row.balance ?? 0, sortable: true },
  { name: 'status', label: 'Status', align: 'left', field: 'status', sortable: true },
  { name: 'actions', label: 'Actions', align: 'right', field: 'actions', style: 'width: 120px' }
]

async function loadItems() {
  loading.value = true
  try {
    const [accData, typeData] = await Promise.all([
      api.accounts.list(),
      api.accountTypes.list().catch(() => [])
    ])
    items.value = Array.isArray(accData) ? accData : []
    if (Array.isArray(typeData) && typeData.length > 0) {
      accountTypeOptions.value = typeData.map(t => ({ label: t.type_name, value: t.id }))
    }
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to load accounts: ' + err.message, position: 'top' })
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  const randomSuffix = Math.floor(1000 + Math.random() * 9000)
  form.value = {
    id: null,
    account_number: `1001-2026-${randomSuffix}`,
    customer_id: 1,
    account_type_id: accountTypeOptions.value[0]?.value || 1,
    status: 'ACTIVE'
  }
  dialogOpen.value = true
}

function openEditDialog(item) {
  isEditing.value = true
  form.value = {
    id: item.id,
    account_number: item.account_number,
    customer_id: item.customer_id ?? item.user_id,
    account_type_id: item.account_type_id,
    status: item.status || 'ACTIVE'
  }
  dialogOpen.value = true
}

async function saveItem() {
  saving.value = true
  try {
    if (isEditing.value) {
      const payload = {
        account_number: form.value.account_number,
        customer_id: Number(form.value.customer_id),
        account_type_id: Number(form.value.account_type_id),
        currency_code: 'PHP',
        status: form.value.status
      }
      const updated = await api.accounts.update(form.value.id, payload)
      const idx = items.value.findIndex(i => i.id === form.value.id)
      if (idx !== -1) items.value[idx] = { ...items.value[idx], ...updated }
      $q.notify({ type: 'positive', message: 'Account updated', position: 'top' })
    } else {
      const payload = {
        account_number: form.value.account_number,
        customer_id: Number(form.value.customer_id),
        account_type_id: Number(form.value.account_type_id),
        currency_code: 'PHP'
      }
      const created = await api.accounts.create(payload)
      items.value.push(created)
      $q.notify({ type: 'positive', message: 'Account opened successfully', position: 'top' })
    }
    dialogOpen.value = false
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Error saving account', position: 'top' })
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
    await api.accounts.delete(itemToDelete.value.id)
    items.value = items.value.filter(i => i.id !== itemToDelete.value.id)
    $q.notify({ type: 'positive', message: 'Account deleted', position: 'top' })
    deleteDialogOpen.value = false
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Failed to delete account', position: 'top' })
  } finally {
    deleting.value = false
  }
}

onMounted(loadItems)
</script>

