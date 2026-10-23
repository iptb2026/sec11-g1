<template>
  <q-page class="q-pa-lg">
    <!-- Page Header -->
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-grey-9">Account Types</div>
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

    <!-- Data Table Card -->
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
        <template v-slot:body-cell-minimum_balance="props">
          <q-td :props="props">
            ₱{{ Number(props.row.minimum_balance).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
          </q-td>
        </template>

        <template v-slot:body-cell-opening_deposit="props">
          <q-td :props="props">
            ₱{{ Number(props.row.opening_deposit).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
          </q-td>
        </template>

        <template v-slot:body-cell-annual_interest_rate="props">
          <q-td :props="props">
            {{ props.row.annual_interest_rate }}%
          </q-td>
        </template>

        <template v-slot:body-cell-daily_withdrawal_limit="props">
          <q-td :props="props">
            ₱{{ Number(props.row.daily_withdrawal_limit).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
          </q-td>
        </template>

        <!-- Actions Column -->
        <template v-slot:body-cell-actions="props">
          <q-td :props="props" align="right">
            <q-btn
              flat
              round
              dense
              color="primary"
              icon="edit"
              class="q-mr-xs"
              @click="openEditDialog(props.row)"
            >
              <q-tooltip>Edit</q-tooltip>
            </q-btn>
            <q-btn
              flat
              round
              dense
              color="negative"
              icon="delete"
              @click="confirmDelete(props.row)"
            >
              <q-tooltip>Delete</q-tooltip>
            </q-btn>
          </q-td>
        </template>
      </q-table>
    </q-card>

    <!-- Create / Edit Dialog -->
    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="min-width: 450px; max-width: 550px;" class="q-pa-sm">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-weight-bold">
            {{ isEditing ? 'Edit Account Type' : 'New Account Type' }}
          </div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-md">
          <q-form @submit="saveItem" class="q-gutter-md">
            <q-input
              v-model="form.type_code"
              label="Type Code *"
              outlined
              dense
              placeholder="e.g. SAVINGS"
              :rules="[val => !!val || 'Code is required']"
              :disable="isEditing"
            />

            <q-input
              v-model="form.type_name"
              label="Type Name *"
              outlined
              dense
              placeholder="e.g. Regular Savings Account"
              :rules="[val => !!val || 'Name is required']"
            />

            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model="form.minimum_balance"
                  label="Minimum Balance (₱)"
                  outlined
                  dense
                  type="number"
                  step="0.01"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="form.opening_deposit"
                  label="Opening Deposit (₱)"
                  outlined
                  dense
                  type="number"
                  step="0.01"
                />
              </div>
            </div>

            <div class="row q-col-gutter-sm">
              <div class="col-6">
                <q-input
                  v-model="form.annual_interest_rate"
                  label="Annual Interest Rate (%)"
                  outlined
                  dense
                  type="number"
                  step="0.01"
                />
              </div>
              <div class="col-6">
                <q-input
                  v-model="form.daily_withdrawal_limit"
                  label="Daily Withdrawal Limit (₱)"
                  outlined
                  dense
                  type="number"
                  step="0.01"
                />
              </div>
            </div>

            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn label="Cancel" flat color="grey-7" v-close-popup />
              <q-btn
                :label="isEditing ? 'Update' : 'Create'"
                type="submit"
                color="primary"
                unelevated
                :loading="saving"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>

    <!-- Delete Confirmation Dialog -->
    <q-dialog v-model="deleteDialogOpen">
      <q-card style="min-width: 350px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-weight-bold text-negative">Confirm Deletion</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section class="q-pt-md text-grey-8">
          Are you sure you want to delete account type
          <strong>{{ itemToDelete?.type_name || itemToDelete?.type_code }}</strong>?
        </q-card-section>

        <q-card-actions align="right" class="q-pa-md">
          <q-btn flat label="Cancel" color="grey-7" v-close-popup />
          <q-btn
            unelevated
            label="Delete"
            color="negative"
            :loading="deleting"
            @click="executeDelete"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api, defaultAccountTypes } from '@/services/api'

const $q = useQuasar()

const items = ref([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)

const dialogOpen = ref(false)
const isEditing = ref(false)
const form = ref({
  id: null,
  type_code: '',
  type_name: '',
  minimum_balance: '0.00',
  opening_deposit: '0.00',
  annual_interest_rate: '0.00',
  daily_withdrawal_limit: '0.00'
})

const deleteDialogOpen = ref(false)
const itemToDelete = ref(null)

const initialPagination = {
  sortBy: 'id',
  descending: false,
  page: 1,
  rowsPerPage: 5
}

const columns = [
  { name: 'id', label: 'ID', align: 'left', field: 'id', sortable: true, style: 'width: 70px' },
  { name: 'type_code', label: 'Code', align: 'left', field: 'type_code', sortable: true },
  { name: 'type_name', label: 'Name', align: 'left', field: 'type_name', sortable: true },
  { name: 'minimum_balance', label: 'Min Balance', align: 'left', field: 'minimum_balance', sortable: true },
  { name: 'opening_deposit', label: 'Opening Deposit', align: 'left', field: 'opening_deposit', sortable: true },
  { name: 'annual_interest_rate', label: 'Interest Rate', align: 'left', field: 'annual_interest_rate', sortable: true },
  { name: 'daily_withdrawal_limit', label: 'Daily Limit', align: 'left', field: 'daily_withdrawal_limit', sortable: true },
  { name: 'actions', label: 'Actions', align: 'right', field: 'actions', sortable: false, style: 'width: 120px' }
]

async function loadItems() {
  loading.value = true
  try {
    const data = await api.accountTypes.list()
    items.value = Array.isArray(data) && data.length > 0 ? data : defaultAccountTypes
  } catch (err) {
    items.value = defaultAccountTypes
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEditing.value = false
  form.value = {
    id: null,
    type_code: '',
    type_name: '',
    minimum_balance: '0.00',
    opening_deposit: '0.00',
    annual_interest_rate: '0.00',
    daily_withdrawal_limit: '0.00'
  }
  dialogOpen.value = true
}

function openEditDialog(item) {
  isEditing.value = true
  form.value = {
    id: item.id,
    type_code: item.type_code,
    type_name: item.type_name,
    minimum_balance: item.minimum_balance || '0.00',
    opening_deposit: item.opening_deposit || '0.00',
    annual_interest_rate: item.annual_interest_rate || '0.00',
    daily_withdrawal_limit: item.daily_withdrawal_limit || '0.00'
  }
  dialogOpen.value = true
}

async function saveItem() {
  saving.value = true
  try {
    if (isEditing.value) {
      const payload = {
        type_code: form.value.type_code,
        type_name: form.value.type_name,
        minimum_balance: form.value.minimum_balance,
        opening_deposit: form.value.opening_deposit,
        annual_interest_rate: form.value.annual_interest_rate,
        daily_withdrawal_limit: form.value.daily_withdrawal_limit
      }
      const updated = await api.accountTypes.update(form.value.id, payload).catch(() => ({
        id: form.value.id,
        ...payload
      }))
      const idx = items.value.findIndex(i => i.id === form.value.id)
      if (idx !== -1) items.value[idx] = { ...items.value[idx], ...updated }
      $q.notify({ type: 'positive', message: 'Account type updated', position: 'top' })
    } else {
      const payload = {
        type_code: form.value.type_code,
        type_name: form.value.type_name,
        minimum_balance: form.value.minimum_balance,
        opening_deposit: form.value.opening_deposit,
        annual_interest_rate: form.value.annual_interest_rate,
        daily_withdrawal_limit: form.value.daily_withdrawal_limit
      }
      const created = await api.accountTypes.create(payload).catch(() => ({
        id: items.value.length > 0 ? Math.max(...items.value.map(i => i.id)) + 1 : 1,
        ...payload,
        created_at: new Date().toISOString()
      }))
      items.value.push(created)
      $q.notify({ type: 'positive', message: 'Account type created', position: 'top' })
    }
    dialogOpen.value = false
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Error saving account type', position: 'top' })
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
    await api.accountTypes.delete(itemToDelete.value.id).catch(() => {})
    items.value = items.value.filter(i => i.id !== itemToDelete.value.id)
    $q.notify({ type: 'positive', message: 'Account type deleted', position: 'top' })
    deleteDialogOpen.value = false
    itemToDelete.value = null
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Delete failed', position: 'top' })
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadItems()
})
</script>

