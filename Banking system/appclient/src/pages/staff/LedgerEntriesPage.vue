<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Ledger Entries</div>
    </div>

    <!-- Read-only: the backend writes a ledger row for every balance change. -->
    <q-table :filter="search" :rows="rows" :columns="tableColumns(columns)" row-key="id" :loading="loading" flat bordered>
      <template #top-right>
        <q-input v-model="search" dense clearable placeholder="Search">
          <template #append><q-icon name="search" /></template>
        </q-input>
      </template>
    </q-table>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { tableColumns } from '@/utils/tableColumns'
import api from '@/services/api'
import { errorMessage } from '@/utils/notify-error'

const $q = useQuasar()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_number', label: 'Account', field: (row) => accountNumberByAccountId.value[row.account_id] || row.account_id, align: 'left' },
  { name: 'transaction_reference', label: 'Reference', field: 'transaction_reference', align: 'left' },
  { name: 'transaction_type', label: 'Type', field: 'transaction_type', align: 'left' },
  { name: 'debit_amount', label: 'Debit', field: 'debit_amount', align: 'right' },
  { name: 'credit_amount', label: 'Credit', field: 'credit_amount', align: 'right' },
  { name: 'balance_after', label: 'Balance After', field: 'balance_after', align: 'right' },
  { name: 'transaction_date', label: 'Date', field: 'transaction_date', align: 'left' },
]

const rows = ref([])
const search = ref('')
const loading = ref(false)
const accountNumberByAccountId = ref({})

async function loadOptions () {
  const { data: accounts } = await api.get('/accounts/')
  accountNumberByAccountId.value = Object.fromEntries(accounts.map((a) => [a.id, a.account_number]))
}

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/ledger-entries/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRows()
  loadOptions()
})
</script>
