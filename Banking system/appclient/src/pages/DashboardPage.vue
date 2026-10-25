<template>
  <q-page>
    <header class="dash-head">
      <div>
        <div class="bank-eyebrow text-gold">{{ today }}</div>
        <h1 class="bank-page-title q-my-xs">{{ greeting }}, {{ auth.firstName || auth.username }}</h1>
        <p class="dash-sub">{{ subtitle }}</p>
      </div>
    </header>

    <div v-if="loading" class="row q-col-gutter-lg">
      <div v-for="n in 4" :key="n" class="col-12 col-sm-6 col-lg-3">
        <q-skeleton height="112px" class="dash-skeleton" />
      </div>
    </div>

    <!-- Customer -->
    <template v-else-if="auth.isCustomer">
      <section class="bank-hero dash-balance">
        <div class="row items-start justify-between">
          <div>
            <div class="bank-eyebrow dash-balance__label">Total available balance</div>
            <div class="dash-balance__amount bank-amount">₱{{ money(totalBalance) }}</div>
            <div class="dash-balance__meta">
              Across {{ myAccounts.length }} account{{ myAccounts.length === 1 ? '' : 's' }}
            </div>
          </div>
          <div class="dash-balance__badge bank-glass">
            <q-icon name="verified_user" size="18px" /> Secured
          </div>
        </div>
        <div class="row q-gutter-sm q-mt-lg">
          <q-btn unelevated no-caps color="white" text-color="primary" icon="credit_card" label="View accounts" to="/my-account" />
          <q-btn outline no-caps color="white" icon="receipt_long" label="Transaction history" to="/my-transactions" />
        </div>
      </section>

      <h2 class="dash-section">Your accounts</h2>
      <div v-if="!myAccounts.length" class="bank-card q-pa-lg text-grey-7">
        No account is registered under your profile yet. Ask a bank staff member to open one for you.
      </div>
      <div v-else class="row q-col-gutter-lg">
        <div v-for="acc in myAccounts" :key="acc.id" class="col-12 col-md-6 col-lg-4">
          <router-link to="/my-account" class="bank-card bank-card--link dash-account">
            <div class="row items-center justify-between">
              <div class="bank-icon-tile dash-tile--blue"><q-icon name="credit_card" size="22px" /></div>
              <q-badge :color="acc.status === 'ACTIVE' ? 'positive' : 'grey-7'">{{ acc.status }}</q-badge>
            </div>
            <div class="dash-account__number tabular">•••• {{ acc.account_number.slice(-4) }}</div>
            <div class="text-caption">Available balance</div>
            <div class="dash-account__amount bank-amount">₱{{ money(acc.available_balance) }}</div>
          </router-link>
        </div>
      </div>
    </template>

    <!-- Admin / staff -->
    <template v-else>
      <div class="row q-col-gutter-lg">
        <div v-for="card in cards" :key="card.label" class="col-12 col-sm-6 col-lg-3">
          <router-link :to="card.to" class="bank-card bank-card--link dash-stat">
            <div class="bank-icon-tile" :class="`dash-tile--${card.tone}`">
              <q-icon :name="card.icon" size="22px" />
            </div>
            <div class="dash-stat__value bank-amount">{{ card.value }}</div>
            <div class="dash-stat__label">{{ card.label }}</div>
          </router-link>
        </div>
      </div>

      <div class="row q-col-gutter-lg q-mt-none">
        <div class="col-12 col-lg-5">
          <section class="bank-hero dash-holdings">
            <div class="bank-eyebrow dash-balance__label">Deposits held</div>
            <div class="dash-balance__amount bank-amount">₱{{ money(totalHeld) }}</div>
            <div class="dash-balance__meta">Available balance across {{ accountCount }} customer accounts</div>
          </section>
        </div>
        <div class="col-12 col-lg-7">
          <section class="bank-card dash-actions">
            <h2 class="dash-section dash-section--flush">Quick actions</h2>
            <div class="row q-col-gutter-md">
              <div v-for="action in quickActions" :key="action.to" class="col-6 col-sm-3">
                <router-link :to="action.to" class="dash-action">
                  <div class="bank-icon-tile" :class="`dash-tile--${action.tone}`"><q-icon :name="action.icon" size="22px" /></div>
                  <span>{{ action.label }}</span>
                </router-link>
              </div>
            </div>
          </section>
        </div>
      </div>
    </template>
  </q-page>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

const auth = useAuthStore()
const loading = ref(true)
const cards = ref([])
const myAccounts = ref([])
const totalHeld = ref(0)
const accountCount = ref(0)

const hour = new Date().getHours()
const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'
const today = new Date().toLocaleDateString('en-PH', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })

const subtitle = computed(() => {
  if (auth.isCustomer) return 'Here is a summary of your money.'
  if (auth.isAdmin) return 'System overview and bank operations.'
  return 'Today’s banking operations at a glance.'
})

const totalBalance = computed(() => myAccounts.value.reduce((sum, a) => sum + Number(a.available_balance), 0))

const quickActions = [
  { label: 'Deposit', to: '/deposits', icon: 'south_west', tone: 'green' },
  { label: 'Withdraw', to: '/withdrawals', icon: 'north_east', tone: 'red' },
  { label: 'Transfer', to: '/transfers', icon: 'swap_horiz', tone: 'blue' },
  { label: 'New account', to: '/accounts', icon: 'person_add', tone: 'gold' },
]

function money (val) {
  return Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function sumBalances (accounts) {
  totalHeld.value = accounts.reduce((sum, a) => sum + Number(a.available_balance), 0)
  accountCount.value = accounts.length
}

async function loadAdminCards () {
  const [roles, users, accounts, banks] = await Promise.all([
    api.get('/roles/'),
    api.get('/users/'),
    api.get('/accounts/'),
    api.get('/banks/'),
  ])
  sumBalances(accounts.data)
  cards.value = [
    { label: 'Users', value: users.data.length, icon: 'group', tone: 'blue', to: '/admin/users' },
    { label: 'Accounts', value: accounts.data.length, icon: 'account_box', tone: 'gold', to: '/accounts' },
    { label: 'Partner banks', value: banks.data.length, icon: 'account_balance', tone: 'navy', to: '/admin/banks' },
    { label: 'Roles', value: roles.data.length, icon: 'admin_panel_settings', tone: 'slate', to: '/admin/roles' },
  ]
}

async function loadStaffCards () {
  const [accounts, deposits, withdrawals, interbank] = await Promise.all([
    api.get('/accounts/'),
    api.get('/deposits/'),
    api.get('/withdrawals/'),
    api.get('/interbank-transfers/'),
  ])
  sumBalances(accounts.data)
  const pending = interbank.data.filter((i) => i.status === 'PROCESSING').length
  cards.value = [
    { label: 'Accounts', value: accounts.data.length, icon: 'account_box', tone: 'blue', to: '/accounts' },
    { label: 'Deposits recorded', value: deposits.data.length, icon: 'south_west', tone: 'green', to: '/deposits' },
    { label: 'Withdrawals recorded', value: withdrawals.data.length, icon: 'north_east', tone: 'red', to: '/withdrawals' },
    { label: 'Interbank pending', value: pending, icon: 'pending_actions', tone: 'gold', to: '/interbank-transfers' },
  ]
}

async function loadCustomer () {
  const { data } = await api.get('/accounts/')
  myAccounts.value = data // the backend only returns the customer's own accounts
}

async function loadCards () {
  try {
    if (auth.isAdmin) await loadAdminCards()
    else if (auth.isStaff || auth.isAuditor) await loadStaffCards()
    else if (auth.isCustomer) await loadCustomer()
  } finally {
    loading.value = false
  }
}

onMounted(loadCards)
</script>

<style scoped>
.dash-head {
  margin-bottom: 24px;
}

.dash-sub {
  color: var(--bank-muted);
  margin: 0;
}

.dash-skeleton {
  border-radius: var(--bank-radius);
}

.dash-section {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 32px 0 14px;
  line-height: 1.3;
}

.dash-section--flush {
  margin-top: 0;
}

/* Balance / holdings hero */
.dash-balance,
.dash-holdings {
  padding: 28px 32px;
}

.dash-holdings {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.dash-balance__label {
  color: #C4D3CD;
}

.dash-balance__amount {
  font-size: clamp(2rem, 4vw, 2.8rem);
  margin: 6px 0 4px;
  line-height: 1.1;
}

.dash-balance__meta {
  color: #C4D3CD;
  font-size: 0.9rem;
}

.dash-balance__badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: 600;
  border-radius: 999px;
}

/* Stat & account cards */
.dash-stat,
.dash-account {
  display: block;
  padding: 20px 22px;
  color: inherit;
  text-decoration: none;
  height: 100%;
}

.dash-stat__value {
  font-size: 2rem;
  margin-top: 14px;
  line-height: 1.1;
}

.dash-stat__label {
  color: var(--bank-muted);
  font-weight: 500;
  margin-top: 2px;
}

.dash-account__number {
  margin: 18px 0 10px;
  font-size: 1.05rem;
  letter-spacing: 0.08em;
  font-weight: 600;
}

.dash-account__amount {
  font-size: 1.6rem;
  line-height: 1.2;
}

/* Icon tile tones */
.dash-tile--blue { background: var(--tipon-sea-tint); color: var(--tipon-sea); }
.dash-tile--green { background: var(--tipon-sea-tint); color: var(--bank-credit); }
.dash-tile--red { background: var(--tipon-bad-tint); color: var(--bank-debit); }
.dash-tile--gold { background: var(--tipon-mango-tint); color: var(--bank-gold-text); }
.dash-tile--navy { background: var(--tipon-ink-tint); color: var(--tipon-ink); }
.dash-tile--slate { background: var(--bank-bg); color: var(--bank-muted); }

/* Quick actions */
.dash-actions {
  padding: 22px 24px;
  height: 100%;
}

.dash-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 16px 8px;
  border-radius: 12px;
  color: var(--bank-text);
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  transition: background-color 0.18s ease;
}

.dash-action:hover {
  background: var(--bank-bg);
}
</style>
