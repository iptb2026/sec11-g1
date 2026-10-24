<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-grey-9">Audit Logs</div>
      <q-btn color="primary" icon="refresh" label="Refresh" outline no-caps @click="loadItems" />
    </div>

    <q-card flat bordered class="bg-white rounded-borders">
      <q-table :rows="items" :columns="columns" row-key="id" :loading="loading" :pagination="initialPagination" flat>
        <template v-slot:body-cell-created_at="props">
          <q-td :props="props">
            {{ new Date(props.row.created_at).toLocaleString() }}
          </q-td>
        </template>
        <template v-slot:body-cell-action="props">
          <q-td :props="props">
            <q-badge color="blue-grey" :label="props.row.action" />
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
const initialPagination = { sortBy: 'id', descending: true, page: 1, rowsPerPage: 10 }

const columns = [
  { name: 'id', label: 'ID', align: 'left', field: 'id', sortable: true, style: 'width: 70px' },
  { name: 'user_id', label: 'User ID', align: 'left', field: 'user_id', sortable: true },
  { name: 'action', label: 'Action', align: 'left', field: 'action', sortable: true },
  { name: 'details', label: 'Details', align: 'left', field: 'details' },
  { name: 'ip_address', label: 'IP Address', align: 'left', field: 'ip_address' },
  { name: 'created_at', label: 'Timestamp', align: 'left', field: 'created_at', sortable: true }
]

async function loadItems() {
  loading.value = true
  try {
    items.value = await api.auditLogs.list()
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadItems)
</script>

