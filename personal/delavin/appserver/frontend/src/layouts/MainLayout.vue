<template>
  <q-layout view="lHh Lpr lFf">
    <!-- Header / Navbar -->
    <q-header elevated class="bg-primary text-white">
      <q-toolbar class="q-px-md">
        <!-- Toggle Left Drawer Button -->
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          class="q-mr-sm"
          @click="toggleLeftDrawer"
        />

        <!-- App Logo & Title -->
        <div class="row items-center cursor-pointer" @click="$router.push('/admin/roles')">
          <q-icon name="account_balance" size="24px" class="q-mr-sm" />
          <q-toolbar-title class="text-weight-bold text-subtitle1" style="font-size: 1.15rem; letter-spacing: 0.2px;">
            Mini Banking System
          </q-toolbar-title>
        </div>

        <q-space />

        <!-- User Role Chip & Profile -->
        <div class="row items-center q-gutter-sm">
          <q-chip
            dense
            color="white"
            text-color="primary"
            icon="business_center"
            class="text-weight-bold q-px-sm"
            style="border-radius: 6px; font-size: 0.8rem;"
          >
            Admin
          </q-chip>

          <span class="text-weight-medium q-mx-xs gt-xs" style="font-size: 0.95rem;">
            Admin User
          </span>

          <q-btn
            flat
            dense
            round
            icon="exit_to_app"
            title="Logout"
            aria-label="Logout"
            @click="handleLogout"
          />
        </div>
      </q-toolbar>
    </q-header>

    <!-- Sidebar Navigation Drawer -->
    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      :width="250"
      class="bg-grey-1"
    >
      <q-scroll-area class="fit">
        <q-list padding class="navigation-list">
          <!-- NAVIGATION -->
          <q-item-label header class="text-grey-7 text-weight-bold text-caption text-uppercase q-pt-sm q-pb-xs">
            Navigation
          </q-item-label>

          <q-item
            clickable
            v-ripple
            to="/admin/dashboard"
            active-class="nav-item-active"
            exact
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="grid_view" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Dashboard</q-item-label>
            </q-item-section>
          </q-item>

          <q-separator class="q-my-sm" />

          <!-- SYSTEM CONFIGURATION -->
          <q-item-label header class="text-grey-7 text-weight-bold text-caption text-uppercase q-pt-xs q-pb-xs">
            System Configuration
          </q-item-label>

          <q-item
            clickable
            v-ripple
            to="/admin/roles"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="verified_user" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Roles</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/account-types"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="account_balance" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Account Types</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/banks"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="apartment" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Banks</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/fee-types"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="local_offer" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Fee Types</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/users"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="group" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Users</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/audit-logs"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="history" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Audit Logs</q-item-label>
            </q-item-section>
          </q-item>

          <q-separator class="q-my-sm" />

          <!-- BANKING OPERATIONS -->
          <q-item-label header class="text-grey-7 text-weight-bold text-caption text-uppercase q-pt-xs q-pb-xs">
            Banking Operations
          </q-item-label>

          <q-item
            clickable
            v-ripple
            to="/admin/accounts"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="badge" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Accounts</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/withdrawal-limits"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="speed" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Withdrawal Limits</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/interest-policies"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="percent" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Interest Policies</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/deposits"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="payments" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Deposits</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/withdrawals"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="remove_circle_outline" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Withdrawals</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/transfers"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="sync_alt" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Transfers</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/interbank-transfers"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="swap_horizontal_circle" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Interbank Transfers</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/fee-records"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="receipt" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Fee Records</q-item-label>
            </q-item-section>
          </q-item>

          <q-item
            clickable
            v-ripple
            to="/admin/interest-records"
            active-class="nav-item-active"
            class="nav-item"
          >
            <q-item-section avatar class="nav-icon-section">
              <q-icon name="trending_up" size="20px" />
            </q-item-section>
            <q-item-section>
              <q-item-label class="nav-label">Interest Records</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <!-- Main Router View Area -->
    <q-page-container class="bg-grey-2" style="min-height: 100vh;">
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useQuasar } from 'quasar'

const $q = useQuasar()
const leftDrawerOpen = ref(true)

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

function handleLogout() {
  $q.notify({
    type: 'info',
    message: 'Logged out successfully',
    position: 'top'
  })
}
</script>

<style scoped>
.navigation-list .nav-item {
  min-height: 38px;
  padding: 6px 16px;
  color: #374151;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.navigation-list .nav-icon-section {
  min-width: 34px;
  padding-right: 8px;
  color: #4b5563;
}

.navigation-list .nav-label {
  font-size: 0.875rem;
  font-weight: 400;
}

.nav-item-active {
  color: #1976d2 !important;
  background-color: #e3f2fd !important;
  font-weight: 600 !important;
  border-left: 3px solid #1976d2;
}

.nav-item-active .nav-icon-section {
  color: #1976d2 !important;
}

.nav-item:hover:not(.nav-item-active) {
  background-color: #f3f4f6;
}
</style>
