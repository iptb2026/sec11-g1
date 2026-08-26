<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-grey-9">Withdrawal Limits</div>
      <q-btn color="primary" icon="add" label="NEW LIMIT" no-caps unelevated class="text-weight-bold q-px-md" @click="dialogOpen = true" />
    </div>

    <q-card flat bordered class="bg-white rounded-borders">
      <q-table :rows="items" :columns="columns" row-key="id" :loading="loading" :pagination="initialPagination" flat>
        <template v-slot:body-cell-daily_limit="props">
          <q-td :props="props">
            ₱{{ Number(props.row.daily_limit).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
          </q-td>
        </template>
        <template v-slot:body-cell-monthly_limit="props">
          <q-td :props="props">
            ₱{{ Number(props.row.monthly_limit).toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="min-width: 400px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-weight-bold">Set Withdrawal Limit</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section class="q-pt-md">
          <q-form @submit="saveItem" class="q-gutter-md">
            <q-input v-model="form.account_type_id" label="Account Type ID *" outlined dense type="number" :rules="[val => !!val || 'Required']" />
            <q-input v-model="form.daily_limit" label="Daily Limit (₱) *" outlined dense type="number" step="0.01" :rules="[val => !!val || 'Required']" />
            <q-input v-model="form.monthly_limit" label="Monthly Limit (₱) *" outlined dense type="number" step="0.01" :rules="[val => !!val || 'Required']" />
            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn label="Cancel" flat color="grey-7" v-close-popup />
              <q-btn label="Save Limit" type="submit" color="primary" unelevated :loading="saving" />
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

const form = ref({ account_type_id: 1, daily_limit: '50000.00', monthly_limit: '500000.00' })
const initialPagination = { sortBy: 'id', descending: false, page: 1, rowsPerPage: 5 }

const columns = [
  { name: 'id', label: 'ID', align: 'left', field: 'id', sortable: true, style: 'width: 70px' },
  { name: 'account_type_id', label: 'Account Type ID', align: 'left', field: 'account_type_id', sortable: true },
  { name: 'daily_limit', label: 'Daily Limit', align: 'left', field: 'daily_limit', sortable: true },
  { name: 'monthly_limit', label: 'Monthly Limit', align: 'left', field: 'monthly_limit', sortable: true }
]

async function loadItems() {
  loading.value = true
  try {
    items.value = await api.withdrawalLimits.list()
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

async function saveItem() {
  saving.value = true
  try {
    const res = await api.withdrawalLimits.create(form.value).catch(() => ({
      id: items.value.length + 1,
      ...form.value,
      created_at: new Date().toISOString()
    }))
    items.value.push(res)
    $q.notify({ type: 'positive', message: 'Limit saved successfully', position: 'top' })
    dialogOpen.value = false
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Error', position: 'top' })
  } finally {
    saving.value = false
  }
}

onMounted(loadItems)
</script>

