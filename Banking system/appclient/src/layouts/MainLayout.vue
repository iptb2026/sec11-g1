<template>
  <q-layout view="lHh Lpr lFf" class="bank-layout">
    <q-header class="bank-topbar">
      <q-toolbar class="bank-topbar__inner">
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Toggle navigation menu"
          class="lt-md q-mr-sm"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />

        <div class="bank-topbar__title">
          <div class="bank-eyebrow text-gold">{{ sectionName }}</div>
          <div class="bank-topbar__page">{{ pageTitle }}</div>
        </div>

        <q-space />

        <div class="bank-secure gt-xs" title="Your session is signed and encrypted">
          <q-icon name="verified_user" size="18px" />
          <span>Secure session</span>
        </div>

        <q-btn flat no-caps class="bank-user" aria-label="Account menu">
          <q-avatar size="36px" class="bank-user__avatar">{{ initials }}</q-avatar>
          <div class="bank-user__text gt-xs">
            <div class="bank-user__name">{{ auth.fullName || auth.username }}</div>
            <div class="bank-user__role">{{ auth.roleName }}</div>
          </div>
          <q-icon name="expand_more" size="20px" class="gt-xs" />
          <q-menu anchor="bottom right" self="top right" :offset="[0, 8]" class="bank-user-menu">
            <q-list style="min-width: 220px">
              <q-item>
                <q-item-section>
                  <q-item-label class="text-weight-medium">{{ auth.fullName || auth.username }}</q-item-label>
                  <q-item-label caption>@{{ auth.username }} · {{ auth.roleName }}</q-item-label>
                </q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable v-close-popup to="/profile">
                <q-item-section avatar><q-icon name="person_outline" /></q-item-section>
                <q-item-section>My profile</q-item-section>
              </q-item>
              <q-item clickable v-close-popup @click="onLogout">
                <q-item-section avatar><q-icon name="logout" color="negative" /></q-item-section>
                <q-item-section class="text-negative">Log out</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above :width="264" class="bank-sidebar">
      <div class="bank-brand">
        <div class="bank-brand__mark"><q-icon name="account_balance" size="22px" /></div>
        <div>
          <div class="bank-brand__name">{{ BANK_NAME }}</div>
          <div class="bank-brand__tag">Banking System</div>
        </div>
      </div>

      <q-scroll-area class="bank-sidebar__scroll">
        <q-list class="bank-nav">
          <q-item clickable to="/" exact class="bank-nav__item">
            <q-item-section avatar><q-icon name="space_dashboard" /></q-item-section>
            <q-item-section>Dashboard</q-item-section>
          </q-item>
          <q-item clickable to="/profile" class="bank-nav__item">
            <q-item-section avatar><q-icon name="person_outline" /></q-item-section>
            <q-item-section>My Profile</q-item-section>
          </q-item>

          <template v-for="group in navGroups" :key="group.title">
            <q-item-label header class="bank-nav__header">{{ group.title }}</q-item-label>
            <q-item
              v-for="link in group.links"
              :key="link.to"
              clickable
              :to="link.to"
              class="bank-nav__item"
            >
              <q-item-section avatar><q-icon :name="link.icon" /></q-item-section>
              <q-item-section>{{ link.label }}</q-item-section>
            </q-item>
          </template>
        </q-list>
      </q-scroll-area>

      <div class="bank-sidebar__foot">
        <q-icon name="lock" size="16px" />
        <span>Protected by encrypted sessions</span>
      </div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth-store'

// The bank's name, shown in the sidebar. Change it here (and in LoginPage.vue).
const BANK_NAME = 'Mini Bank'

const leftDrawerOpen = ref(false)
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const ADMIN_LINKS = [
  { to: '/admin/roles', label: 'Roles', icon: 'admin_panel_settings' },
  { to: '/admin/account-types', label: 'Account Types', icon: 'category' },
  { to: '/admin/banks', label: 'Banks', icon: 'account_balance' },
  { to: '/admin/fee-types', label: 'Fee Types', icon: 'sell' },
  { to: '/admin/users', label: 'Users', icon: 'group' },
  { to: '/admin/audit-logs', label: 'Audit Logs', icon: 'history' },
]

const OPERATIONS_LINKS = [
  { to: '/accounts', label: 'Accounts', icon: 'account_box' },
  { to: '/deposits', label: 'Deposits', icon: 'south_west' },
  { to: '/withdrawals', label: 'Withdrawals', icon: 'north_east' },
  { to: '/transfers', label: 'Transfers', icon: 'swap_horiz' },
  { to: '/interbank-transfers', label: 'Interbank Transfers', icon: 'public' },
  { to: '/withdrawal-limits', label: 'Withdrawal Limits', icon: 'speed' },
  { to: '/interest-policies', label: 'Interest Policies', icon: 'percent' },
  { to: '/fee-records', label: 'Fee Records', icon: 'receipt_long' },
  { to: '/interest-records', label: 'Interest Records', icon: 'savings' },
  { to: '/ledger-entries', label: 'Ledger', icon: 'menu_book' },
]

const CUSTOMER_LINKS = [
  { to: '/my-account', label: 'My Accounts', icon: 'credit_card' },
  { to: '/my-transactions', label: 'Transactions', icon: 'receipt_long' },
]

const navGroups = computed(() => {
  const groups = []
  if (auth.isAdmin) groups.push({ title: 'Administration', links: ADMIN_LINKS })
  if (auth.isAdmin || auth.isStaff) groups.push({ title: 'Banking Operations', links: OPERATIONS_LINKS })
  if (auth.isCustomer) groups.push({ title: 'My Banking', links: CUSTOMER_LINKS })
  // Same pages as an admin, but the pages hide New/Edit/Delete for auditors.
  if (auth.isAuditor) {
    groups.push({ title: 'Administration (read-only)', links: ADMIN_LINKS })
    groups.push({ title: 'Banking Operations (read-only)', links: OPERATIONS_LINKS })
  }
  return groups
})

// Title shown in the top bar, from the link that matches the current page.
const currentLink = computed(() => {
  for (const group of navGroups.value) {
    const link = group.links.find((l) => route.path.startsWith(l.to))
    if (link) return { group: group.title, label: link.label }
  }
  return null
})
const isProfile = computed(() => route.path.startsWith('/profile'))
const pageTitle = computed(() => (isProfile.value ? 'My Profile' : currentLink.value?.label || 'Dashboard'))
const sectionName = computed(() => (isProfile.value ? 'Account' : currentLink.value?.group || 'Overview'))

const initials = computed(() => {
  const parts = [auth.firstName, auth.lastName].filter(Boolean)
  const source = parts.length ? parts : [auth.username || '?']
  return source.map((p) => p[0]).join('').slice(0, 2).toUpperCase()
})

async function onLogout () {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.bank-layout {
  background: var(--bank-bg);
}

/* --- Top bar --- */
.bank-topbar {
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: var(--bank-text);
  border-bottom: 1px solid var(--bank-border);
}

.bank-topbar__inner {
  min-height: 68px;
  padding: 0 24px;
}

.bank-topbar__title {
  line-height: 1.2;
}

.bank-topbar__page {
  font-size: 1.05rem;
  font-weight: 600;
}

.bank-secure {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  margin-right: 12px;
  border-radius: 999px;
  background: #ECFDF5;
  color: var(--bank-credit);
  font-size: 0.8rem;
  font-weight: 600;
}

.bank-user {
  padding: 4px 8px;
  border-radius: 12px;
}

.bank-user__avatar {
  background: linear-gradient(135deg, var(--bank-blue-800), var(--bank-navy-900));
  color: #fff;
  font-weight: 600;
  font-size: 0.85rem;
}

.bank-user__text {
  text-align: left;
  margin: 0 6px 0 10px;
  line-height: 1.2;
}

.bank-user__name {
  font-weight: 600;
  font-size: 0.9rem;
}

.bank-user__role {
  font-size: 0.75rem;
  color: var(--bank-muted);
  font-weight: 500;
}

/* --- Sidebar --- */
.bank-layout :deep(.q-drawer) {
  background: linear-gradient(180deg, var(--bank-navy-900) 0%, var(--bank-navy-950) 100%);
  color: #CBD5E1;
  display: flex;
  flex-direction: column;
}

.bank-layout :deep(.q-drawer__content) {
  display: flex;
  flex-direction: column;
}

.bank-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 20px 18px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
}

.bank-brand__mark {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--bank-navy-900);
  background: linear-gradient(135deg, var(--bank-gold-light), var(--bank-gold));
  box-shadow: 0 6px 18px rgba(202, 138, 4, 0.35);
}

.bank-brand__name {
  color: #fff;
  font-weight: 700;
  font-size: 1.05rem;
  letter-spacing: -0.01em;
}

.bank-brand__tag {
  color: #94A3B8;
  font-size: 0.75rem;
}

.bank-sidebar__scroll {
  flex: 1;
}

.bank-nav {
  padding: 12px 12px 20px;
}

.bank-nav__header {
  color: #64748B;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 18px 12px 8px;
}

.bank-nav__item {
  border-radius: 10px;
  min-height: 42px;
  margin-bottom: 2px;
  color: #CBD5E1;
  font-weight: 500;
  font-size: 0.9rem;
  transition: background-color 0.18s ease, color 0.18s ease;
}

.bank-nav__item :deep(.q-item__section--avatar) {
  min-width: 36px;
  color: #94A3B8;
}

.bank-nav__item:hover {
  background: rgba(148, 163, 184, 0.12);
  color: #fff;
}

.bank-nav__item.q-router-link--active {
  background: rgba(37, 99, 235, 0.22);
  color: #fff;
  box-shadow: inset 3px 0 0 var(--bank-gold-light);
}

.bank-nav__item.q-router-link--active :deep(.q-item__section--avatar) {
  color: var(--bank-gold-light);
}

.bank-sidebar__foot {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  font-size: 0.75rem;
  color: #94A3B8;
  border-top: 1px solid rgba(148, 163, 184, 0.16);
}
</style>
