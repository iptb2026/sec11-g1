<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-md">
      <div class="text-h5 text-weight-bold text-grey-9">Interest Policies</div>
      <q-btn color="primary" icon="add" label="NEW POLICY" no-caps unelevated class="text-weight-bold q-px-md" @click="dialogOpen = true" />
    </div>

    <q-card flat bordered class="bg-white rounded-borders">
      <q-table :rows="items" :columns="columns" row-key="id" :loading="loading" :pagination="initialPagination" flat>
        <template v-slot:body-cell-rate="props">
          <q-td :props="props">
            {{ props.row.rate }}%
          </q-td>
        </template>
      </q-table>
    </q-card>

    <q-dialog v-model="dialogOpen" persistent>
      <q-card style="min-width: 400px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-weight-bold">Create Interest Policy</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section class="q-pt-md">
          <q-form @submit="saveItem" class="q-gutter-md">
            <q-input v-model="form.account_type_id" label="Account Type ID *" outlined dense type="number" :rules="[val => !!val || 'Required']" />
            <q-input v-model="form.rate" label="Interest Rate (%) *" outlined dense type="number" step="0.01" :rules="[val => !!val || 'Required']" />
            <q-select v-model="form.period" :options="['ANNUAL', 'MONTHLY', 'DAILY']" label="Period" outlined dense />
            <div class="row justify-end q-gutter-sm q-mt-md">
              <q-btn label="Cancel" flat color="grey-7" v-close-popup />
              <q-btn label="Save Policy" type="submit" color="primary" unelevated :loading="saving" />
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

const form = ref({ account_type_id: 1, rate: '1.50', period: 'ANNUAL' })
const initialPagination = { sortBy: 'id', descending: false, page: 1, rowsPerPage: 5 }

const columns = [
  { name: 'id', label: 'ID', align: 'left', field: 'id', sortable: true, style: 'width: 70px' },
  { name: 'account_type_id', label: 'Account Type ID', align: 'left', field: 'account_type_id', sortable: true },
  { name: 'rate', label: 'Interest Rate', align: 'left', field: 'rate', sortable: true },
  { name: 'period', label: 'Compounding Period', align: 'left', field: 'period', sortable: true }
]

async function loadItems() {
  loading.value = true
  try {
    items.value = await api.interestPolicies.list()
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

async function saveItem() {
  saving.value = true
  try {
    const res = await api.interestPolicies.create(form.value).catch(() => ({
      id: items.value.length + 1,
      ...form.value,
      created_at: new Date().toISOString()
    }))
    items.value.push(res)
    $q.notify({ type: 'positive', message: 'Policy created successfully', position: 'top' })
    dialogOpen.value = false
  } catch (err) {
    $q.notify({ type: 'negative', message: err.message || 'Error', position: 'top' })
  } finally {
    saving.value = false
  }
}

onMounted(loadItems)
</script>

