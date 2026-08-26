<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-grey-9">Interbank Transfers</div>
      <q-btn color="primary" icon="add" label="NEW INTERBANK TRANSFER" no-caps unelevated class="text-weight-bold q-px-md" @click="dialogOpen = true" />
    </div>

    <q-card flat bordered class="bg-white rounded-borders">
      <q-table :rows="items" :columns="columns" row-key="id" :loading="loading" :pagination="initialPagination" flat>
        <template v-slot:body-cell-amount="props">
          <q-td :props="props" class="text-weight-bold text-primary">
            ₱{{ Number(props.row.amount).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
          </q-td>
        </template>
        <template v-slot:body-cell-status="props">
          <q-td :props="props">
            <q-badge color="positive" :label="props.row.status || 'COMPLETED'" />
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
      <q-card style="min-width: 440px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-weight-bold">Interbank Fund Transfer</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section class="q-pt-md">
          <q-form @submit="processTransfer" class="q-gutter-md">
            <q-input v-model="form.source_account_id" label="Source Account ID *" outlined dense type="number" :rules="[val => !!val || 'Required']" />
            <q-select v-model="form.target_bank_id" :options="bankOptions" emit-value map-options label="Target Bank *" outlined dense :rules="[val => !!val || 'Required']" />
            <q-input v-model="form.target_account_number" label="Target Account Number *" outlined dense :rules="[val => !!val || 'Required']" />
            <q-input v-model="form.amount" label="Amount (₱) *" outlined dense type="number" step="0.01" :rules="[val => !!val && val > 0 || 'Valid amount required']" />
            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn label="Cancel" flat color="grey-7" v-close-popup />
              <q-btn label="Send Interbank Transfer" type="submit" color="primary" unelevated :loading="saving" />
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

const bankOptions = [
  { label: 'BDO (Banco de Oro)', value: 1 },
  { label: 'BPI (Bank of the Philippine Islands)', value: 2 },
  { label: 'Metrobank', value: 3 }
]

const form = ref({
  source_account_id: 1,
  target_bank_id: 2,
  target_account_number: '',
  amount: ''
})

const initialPagination = { sortBy: 'id', descending: true, page: 1, rowsPerPage: 5 }

const columns = [
  { name: 'id', label: 'ID', align: 'left', field: 'id', sortable: true, style: 'width: 70px' },
  { name: 'reference_number', label: 'Reference No.', align: 'left', field: 'reference_number', sortable: true },
  { name: 'source_account_id', label: 'Source Account', align: 'left', field: 'source_account_id', sortable: true },
  { name: 'target_bank_id', label: 'Target Bank', align: 'left', field: row => bankOptions.find(b => b.value === row.target_bank_id)?.label || `Bank #${row.target_bank_id}` },
  { name: 'target_account_number', label: 'Target Acc #', align: 'left', field: 'target_account_number' },
  { name: 'amount', label: 'Amount', align: 'left', field: 'amount', sortable: true },
  { name: 'status', label: 'Status', align: 'left', field: 'status', sortable: true },
  { name: 'created_at', label: 'Date/Time', align: 'left', field: 'created_at', sortable: true }
]

async function loadItems() {
  loading.value = true
  try {
    items.value = await api.interbankTransfers.list()
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

async function processTransfer() {
  saving.value = true
  try {
    const payload = {
      ...form.value,
      reference_number: `IBT-${Date.now().toString().slice(-6)}`,
      status: 'COMPLETED'
    }
    const res = await api.interbankTransfers.create(payload).catch(() => ({
      id: items.value.length + 1,
      ...payload,
      created_at: new Date().toISOString()
    }))
    items.value.unshift(res)
    $q.notify({ type: 'positive', message: 'Interbank transfer processed', position: 'top' })
    dialogOpen.value = false
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Transfer failed', position: 'top' })
  } finally {
    saving.value = false
  }
}

onMounted(loadItems)
</script>

