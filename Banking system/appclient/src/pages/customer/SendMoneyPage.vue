<template>
  <q-page>
    <div class="row items-center q-mb-md">
      <div class="text-h5">Send Money</div>
    </div>

    <div v-if="loading" class="send-wrap"><q-skeleton height="320px" class="send-skeleton" /></div>

    <div v-else-if="accounts.length === 0" class="bank-card q-pa-lg text-grey-7 send-wrap">
      No account is registered under your profile yet. Ask a bank staff member to open one for you.
    </div>

    <!-- Sent: the receipt, with the balance read back from the server -->
    <section v-else-if="receipt" class="bank-card send-wrap send-receipt">
      <div class="bank-icon-tile send-receipt__tile"><q-icon name="check" size="26px" /></div>
      <h2>Money sent</h2>
      <div class="send-receipt__amount bank-amount">₱{{ format(receipt.amount) }}</div>
      <dl class="send-receipt__rows">
        <dt>To account</dt><dd>{{ receipt.to }}</dd>
        <dt>From account</dt><dd>{{ receipt.from }}</dd>
        <dt>Reference</dt><dd class="tabular">{{ receipt.reference }}</dd>
        <dt>Date</dt><dd>{{ receipt.date }}</dd>
        <dt>New balance</dt><dd class="bank-amount">₱{{ format(receipt.newBalance) }}</dd>
      </dl>
      <div class="row q-gutter-sm q-mt-md">
        <q-btn unelevated no-caps color="primary" icon="receipt_long" label="View transactions" to="/my-transactions" />
        <q-btn outline no-caps color="primary" icon="send" label="Send again" @click="startOver" />
      </div>
    </section>

    <!-- The form -->
    <section v-else class="bank-card send-wrap send-form">
      <q-form @submit="confirmSend">
        <q-select
          v-model="form.source_account_id"
          :options="accountOptions"
          label="From account"
          emit-value
          map-options
          outlined
          :rules="[required]"
        >
          <template #option="scope">
            <q-item v-bind="scope.itemProps">
              <q-item-section>
                <q-item-label>{{ scope.opt.label }}</q-item-label>
                <q-item-label caption>Available ₱{{ format(scope.opt.balance) }}</q-item-label>
              </q-item-section>
            </q-item>
          </template>
        </q-select>
        <div v-if="selected" class="send-hint">Available balance: <b>₱{{ format(selected.available_balance) }}</b></div>

        <q-input
          v-model="form.destination_account_number"
          label="To account number"
          outlined
          inputmode="numeric"
          hint="The 10-digit account number of the person you're paying"
          :rules="[required, (val) => /^\d{10}$/.test(String(val).trim()) || 'Enter a 10-digit account number']"
          lazy-rules
        />
        <q-input
          v-model.number="form.amount"
          label="Amount (₱)"
          type="number"
          step="0.01"
          min="0.01"
          outlined
          :rules="[positiveAmount, (val) => !selected || Number(val) <= Number(selected.available_balance) || 'More than your available balance']"
          lazy-rules
        />
        <q-input v-model="form.remarks" label="Note (optional)" outlined maxlength="100" />

        <q-banner v-if="errorText" dense rounded class="send-error" role="alert">
          <template #avatar><q-icon name="error_outline" /></template>
          {{ errorText }}
        </q-banner>

        <q-btn type="submit" label="Send money" icon="send" color="primary" size="lg" class="full-width q-mt-sm" :loading="sending" unelevated no-caps />
      </q-form>
    </section>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import api from '@/services/api'
import { errorMessage } from '@/utils/notify-error'
import { formatDate } from '@/utils/tableColumns'
import { positiveAmount, required } from '@/utils/validation'

const $q = useQuasar()
const accounts = ref([])
const loading = ref(true)
const sending = ref(false)
const errorText = ref('')
const receipt = ref(null)

const emptyForm = () => ({ source_account_id: accounts.value[0]?.id ?? null, destination_account_number: '', amount: null, remarks: '' })
const form = ref(emptyForm())

const accountOptions = computed(() => accounts.value
  .filter((a) => a.status === 'ACTIVE')
  .map((a) => ({ label: a.account_number, value: a.id, balance: a.available_balance })))
const selected = computed(() => accounts.value.find((a) => a.id === form.value.source_account_id))

function format (val) {
  return Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// The backend only returns the customer's own accounts.
async function loadAccounts () {
  const { data } = await api.get('/accounts/')
  accounts.value = data
}

function confirmSend () {
  errorText.value = ''
  const to = String(form.value.destination_account_number).trim()
  $q.dialog({
    title: 'Send money?',
    message: `Send ₱${format(form.value.amount)} from ${selected.value.account_number} to ${to}?`,
    cancel: true,
    persistent: true,
    ok: { label: 'Send', color: 'primary', unelevated: true, noCaps: true },
  }).onOk(send)
}

async function send () {
  sending.value = true
  try {
    const { data } = await api.post('/transfers/', {
      source_account_id: form.value.source_account_id,
      destination_account_number: String(form.value.destination_account_number).trim(),
      amount: form.value.amount,
      remarks: form.value.remarks || null,
    })
    // Read the balance back from the server, so the receipt shows what is stored.
    await loadAccounts()
    const from = accounts.value.find((a) => a.id === data.source_account_id)
    receipt.value = {
      amount: data.amount,
      to: String(form.value.destination_account_number).trim(),
      from: from?.account_number,
      reference: data.transfer_reference,
      date: formatDate(data.created_at).replace('\n', ' '),
      newBalance: from?.available_balance,
    }
    $q.notify({ type: 'positive', message: `Sent ₱${format(data.amount)}` })
  } catch (err) {
    errorText.value = errorMessage(err, 'Sending failed')
  } finally {
    sending.value = false
  }
}

function startOver () {
  receipt.value = null
  form.value = emptyForm()
}

onMounted(async () => {
  try {
    await loadAccounts()
    form.value = emptyForm()
  } catch (err) {
    $q.notify({ type: 'negative', message: errorMessage(err, 'Failed to load your accounts') })
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.send-wrap {
  max-width: 520px;
}

.send-skeleton {
  border-radius: var(--bank-radius);
}

.send-form {
  padding: 1.4rem;
}

.send-form .q-form {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.send-hint {
  margin: -10px 0 8px;
  font-size: 0.85rem;
  color: var(--bank-muted);
}

.send-error {
  background: var(--tipon-bad-tint);
  color: var(--bank-debit);
  border: 1.5px solid var(--bank-debit);
}

.send-receipt {
  padding: 1.6rem 1.4rem;
}

.send-receipt__tile {
  background: var(--tipon-sea-tint);
  color: var(--tipon-sea);
}

.send-receipt h2 {
  font-family: var(--tipon-display);
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0.8rem 0 0.2rem;
}

.send-receipt__amount {
  font-size: 2.2rem;
  color: var(--bank-debit);
}

.send-receipt__rows {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 6px 16px;
  margin: 1rem 0 0;
}

.send-receipt__rows dt {
  color: var(--bank-muted);
}

.send-receipt__rows dd {
  margin: 0;
  text-align: right;
  font-weight: 600;
}
</style>
