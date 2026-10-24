<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Audit Logs</div>
    </div>

    <!-- Read-only: the backend logs every create/update/delete by itself. -->
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
  { name: 'user_id', label: 'User ID', field: 'user_id', align: 'left' },
  { name: 'action_type', label: 'Action', field: 'action_type', align: 'left' },
  { name: 'entity_name', label: 'Entity', field: 'entity_name', align: 'left' },
  { name: 'entity_id', label: 'Entity ID', field: 'entity_id', align: 'left' },
  { name: 'ip_address', label: 'IP Address', field: 'ip_address', align: 'left' },
  { name: 'action_timestamp', label: 'Timestamp', field: 'action_timestamp', align: 'left' },
]

const rows = ref([])
const search = ref('')
const loading = ref(false)

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/audit-logs/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

onMounted(loadRows)
</script>
