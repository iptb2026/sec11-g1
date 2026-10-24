<template>
  <q-page>
    <div class="row items-center q-mb-md">
      <div class="text-h5">My Accounts</div>
    </div>

    <div v-if="loading" class="row q-col-gutter-lg">
      <div class="col-12 col-md-6"><q-skeleton height="240px" class="acc-skeleton" /></div>
    </div>

    <div v-else-if="accounts.length === 0" class="bank-card q-pa-lg text-grey-7">
      No account is registered under your profile yet. Ask a bank staff member to open one for you.
    </div>

    <div v-else class="row q-col-gutter-lg">
      <div v-for="acc in accounts" :key="acc.id" class="col-12 col-md-6">
        <article class="acc">
          <div class="acc-card bank-hero">
            <div class="row items-center justify-between">
              <span class="bank-eyebrow acc-card__muted">{{ acc.currency_code }} Account</span>
              <q-icon name="contactless" size="22px" aria-hidden="true" />
            </div>
            <div class="acc-card__chip" aria-hidden="true" />
            <div class="acc-card__number tabular">{{ groupNumber(acc.account_number) }}</div>
            <div class="row items-end justify-between">
              <div>
                <div class="acc-card__muted acc-card__label">Available balance</div>
                <div class="acc-card__amount bank-amount">₱{{ format(acc.available_balance) }}</div>
              </div>
              <q-badge :color="acc.status === 'ACTIVE' ? 'positive' : 'grey-7'">{{ acc.status }}</q-badge>
            </div>
          </div>

          <dl class="acc-details bank-card">
            <div><dt>Ledger balance</dt><dd class="bank-amount">₱{{ format(acc.ledger_balance) }}</dd></div>
            <div><dt>Branch</dt><dd>{{ acc.branch_code || '—' }}</dd></div>
            <div><dt>Opened</dt><dd>{{ formatDate(acc.opened_at) }}</dd></div>
            <div><dt>Account number</dt><dd class="tabular">{{ acc.account_number }}</dd></div>
          </dl>
        </article>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/services/api'

const accounts = ref([])
const loading = ref(true)

function format (val) {
  return Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// "1000000001" -> "1000 0000 01" like a card number; other formats are shown as they are.
function groupNumber (num) {
  const text = String(num)
  return /^\d+$/.test(text) ? text.replace(/(\d{4})(?=\d)/g, '$1 ') : text
}

function formatDate (val) {
  return val ? new Date(val).toLocaleDateString('en-PH', { month: 'long', day: 'numeric', year: 'numeric' }) : '—'
}

async function loadAccounts () {
  try {
    const { data } = await api.get('/accounts/')
    accounts.value = data // the backend only returns the customer's own accounts
  } finally {
    loading.value = false
  }
}

onMounted(loadAccounts)
</script>

<style scoped>
.acc-skeleton {
  border-radius: 20px;
}

.acc-card {
  aspect-ratio: 1.7;
  max-height: 260px;
  width: 100%;
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: none;
}

.acc-card__muted {
  color: #C4D3CD;
}

.acc-card__chip {
  width: 46px;
  height: 34px;
  border-radius: 8px;
  background: var(--tipon-mango);
}

.acc-card__number {
  font-size: 1.35rem;
  letter-spacing: 0.12em;
  font-weight: 500;
}

.acc-card__label {
  font-size: 0.75rem;
}

.acc-card__amount {
  font-size: 1.9rem;
  line-height: 1.15;
}

.acc-details {
  margin: 14px 0 0;
  padding: 16px 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 24px;
}

.acc-details dt {
  font-size: 0.75rem;
  color: var(--bank-muted);
  font-weight: 500;
}

.acc-details dd {
  margin: 2px 0 0;
  font-weight: 600;
}
</style>
