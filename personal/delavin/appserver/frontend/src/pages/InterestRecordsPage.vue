<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-grey-9">Interest Accrual Records</div>
      <q-btn color="primary" icon="refresh" label="Refresh" outline no-caps @click="loadItems" />
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
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'

const items = ref([])
const loading = ref(false)
const initialPagination = { sortBy: 'id', descending: true, page: 1, rowsPerPage: 5 }

const columns = [
  { name: 'id', label: 'ID', align: 'left', field: 'id', sortable: true, style: 'width: 70px' },
  { name: 'account_id', label: 'Account ID', align: 'left', field: 'account_id', sortable: true },
  { name: 'amount', label: 'Accrued Interest', align: 'left', field: 'amount', sortable: true },
  { name: 'period_start', label: 'Period Start', align: 'left', field: 'period_start', sortable: true },
  { name: 'period_end', label: 'Period End', align: 'left', field: 'period_end', sortable: true },
  { name: 'created_at', label: 'Processed Date', align: 'left', field: 'created_at', sortable: true }
]

async function loadItems() {
  loading.value = true
  try {
    items.value = await api.interestRecords.list()
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadItems)
</script>

