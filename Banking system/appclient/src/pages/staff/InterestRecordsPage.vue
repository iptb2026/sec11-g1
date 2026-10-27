<template>
  <q-page class="q-pa-md">
    <div class="row items-center q-mb-md">
      <div class="text-h5">Interest Records</div>
      <q-space />
      <q-btn v-if="canWrite" color="primary" icon="add" label="New" @click="openCreate" />
    </div>

    <q-table :filter="search" :rows="rows" :columns="tableColumns(columns, canWrite)" row-key="id" :loading="loading" :pagination="{ rowsPerPage: 10 }" flat bordered>
      <template #top-right>
        <q-input v-model="search" dense clearable placeholder="Search">
          <template #append><q-icon name="search" /></template>
        </q-input>
      </template>
      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn dense flat round icon="delete" aria-label="Delete" color="negative" @click="removeRow(props.row)" />
        </q-td>
      </template>
    </q-table>

    <!-- balance_before / balance_after are computed by the backend, not part of this form -->
    <q-dialog v-model="showDialog">
      <q-card style="width: 420px">
        <q-form @submit="save">
          <q-card-section>
            <div class="text-h6">New Interest Record</div>
          </q-card-section>

          <q-card-section class="q-gutter-md">
            <q-select
              v-model="form.account_id" :rules="[required]" lazy-rules
              label="Account"
              filled
              emit-value
              map-options
              :options="accountOptions"
            />
            <q-select
              v-model="form.policy_id" :rules="[required]" lazy-rules
              label="Interest Policy"
              filled
              emit-value
              map-options
              :options="policyOptions"
            />
            <div class="text-caption text-grey-7">
              The interest is calculated by the server from the account balance and the policy's rate.
            </div>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat label="Cancel" v-close-popup />
            <q-btn color="primary" label="Save" type="submit" />
          </q-card-actions>
        </q-form>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { tableColumns } from '@/utils/tableColumns'
import api from '@/services/api'
import { useCanWrite } from '@/utils/permissions'
import { errorMessage } from '@/utils/notify-error'
import { required } from '@/utils/validation'

const $q = useQuasar()
const canWrite = useCanWrite()

const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'account_number', label: 'Account', field: (row) => accountNumberByAccountId.value[row.account_id] || row.account_id, align: 'left' },
  { name: 'policy', label: 'Policy', field: (row) => policyNameById.value[row.policy_id] || row.policy_id, align: 'left' },
  { name: 'amount_credited', label: 'Amount Credited', field: 'amount_credited', align: 'right' },
  { name: 'balance_before', label: 'Balance Before', field: 'balance_before', align: 'right' },
  { name: 'balance_after', label: 'Balance After', field: 'balance_after', align: 'right' },
  { name: 'credited_at', label: 'Credited At', field: 'credited_at', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'actions', align: 'right' },
]

const rows = ref([])
const search = ref('')
const accountOptions = ref([])
const policyOptions = ref([])
const accountNumberByAccountId = ref({})
const policyNameById = ref({})
const loading = ref(false)
const showDialog = ref(false)
const emptyForm = () => ({ account_id: null, policy_id: null })
const form = ref(emptyForm())

async function loadRows () {
  loading.value = true
  try {
    const { data } = await api.get('/interest-records/')
    rows.value = data
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load data') })
  } finally {
    loading.value = false
  }
}

async function loadOptions () {
  const { data: accounts } = await api.get('/accounts/')
  accountOptions.value = accounts.map((a) => ({ label: a.account_number, value: a.id }))
  accountNumberByAccountId.value = Object.fromEntries(accounts.map((a) => [a.id, a.account_number]))

  const { data: policies } = await api.get('/interest-policies/')
  policyOptions.value = policies.map((p) => ({ label: p.policy_name, value: p.id }))
  policyNameById.value = Object.fromEntries(policies.map((p) => [p.id, p.policy_name]))
}

function openCreate () {
  form.value = emptyForm()
  showDialog.value = true
}

async function save () {
  try {
    await api.post('/interest-records/', form.value)
    showDialog.value = false
    $q.notify({ type: 'positive', message: 'Interest record created' })
    loadRows()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Save failed') })
  }
}

function removeRow (row) {
  $q.dialog({
    title: 'Confirm Delete',
    message: `Delete interest record #${row.id}? The interest is taken back out of the account.`,
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    try {
      await api.delete(`/interest-records/${row.id}`)
      $q.notify({ type: 'positive', message: 'Interest record deleted' })
      loadRows()
    } catch (err) {
      $q.notify({ type: 'negative', message: errorMessage(err, 'Delete failed') })
    }
  })
}

onMounted(() => {
  loadRows()
  loadOptions()
})
</script>
