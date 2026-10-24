<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-grey-9">Deposit Transactions</div>
      <q-btn color="primary" icon="add" label="NEW DEPOSIT" no-caps unelevated class="text-weight-bold q-px-md" @click="dialogOpen = true" />
    </div>

    <q-card flat bordered class="bg-white rounded-borders">
      <q-table :rows="items" :columns="columns" row-key="id" :loading="loading" :pagination="initialPagination" flat>
        <template v-slot:body-cell-amount="props">
          <q-td :props="props" class="text-weight-bold text-positive">
            +₱{{ Number(props.row.amount).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
          </q-td>
        </template>
        <template v-slot:body-cell-created_at="props">
          <q-td :props="props">
            {{ new Date(props.row.created_at).toLocaleString() }}
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="min-width: 400px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-weight-bold">Process Deposit</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section class="q-pt-md">
          <q-form @submit="processDeposit" class="q-gutter-md">
            <q-input v-model="form.account_id" label="Account ID *" outlined dense type="number" :rules="[val => !!val || 'Required']" />
            <q-input v-model="form.amount" label="Amount (₱) *" outlined dense type="number" step="0.01" :rules="[val => !!val && val > 0 || 'Valid amount required']" />
            <q-select v-model="form.channel" :options="['CASH', 'ATM', 'ONLINE', 'INTERBANK']" label="Channel" outlined dense />
            <q-input v-model="form.reference_number" label="Reference Number" outlined dense />
            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn label="Cancel" flat color="grey-7" v-close-popup />
              <q-btn label="Submit Deposit" type="submit" color="primary" unelevated :loading="saving" />
            </div>
          </q-form>
        </q-card-section>
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
const dialogOpen = ref(false)

const form = ref({
  account_id: 1,
  amount: '',
  channel: 'CASH',
  reference_number: ''
})

const initialPagination = { sortBy: 'id', descending: true, page: 1, rowsPerPage: 5 }

const columns = [
  { name: 'id', label: 'ID', align: 'left', field: 'id', sortable: true, style: 'width: 70px' },
  { name: 'reference_number', label: 'Reference No.', align: 'left', field: 'reference_number', sortable: true },
  { name: 'account_id', label: 'Account ID', align: 'left', field: 'account_id', sortable: true },
  { name: 'amount', label: 'Amount', align: 'left', field: row => `₱${Number(row.amount).toLocaleString('en-US', { minimumFractionDigits: 2 })}`, sortable: true },
  { name: 'channel', label: 'Channel', align: 'left', field: row => row.deposit_channel || row.channel, sortable: true },
  { name: 'created_at', label: 'Date/Time', align: 'left', field: row => new Date(row.created_at || row.transaction_date).toLocaleString(), sortable: true }
]

async function loadItems() {
  loading.value = true
  try {
    const data = await api.deposits.list()
    items.value = Array.isArray(data) ? data : []
  } catch (err) {
    $q.notify({ type: 'negative', message: 'Failed to load deposits: ' + err.message, position: 'top' })
  } finally {
    loading.value = false
  }
}

async function processDeposit() {
  saving.value = true
  try {
    const refNum = form.value.reference_number || `DEP-${Date.now().toString().slice(-6)}`
    const payload = {
      account_id: Number(form.value.account_id),
      amount: form.value.amount,
      deposit_channel: form.value.channel || 'CASH',
      reference_number: refNum
    }
    const res = await api.deposits.create(payload)
    items.value.unshift(res)
    $q.notify({ type: 'positive', message: 'Deposit recorded successfully', position: 'top' })
    dialogOpen.value = false
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Deposit failed', position: 'top' })
  } finally {
    saving.value = false
  }
}

onMounted(loadItems)
</script>

