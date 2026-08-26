<template>
  <q-page class="q-pa-lg">
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <div class="text-h5 text-weight-bold text-grey-9">Dashboard Overview</div>
        <div class="text-caption text-grey-7">Mini Banking System Administration Console</div>
      </div>
      <q-btn
        color="primary"
        icon="refresh"
        label="Refresh"
        no-caps
        outline
        @click="refreshData"
      />
    </div>

    <!-- Metric Cards Row -->
    <div class="row q-col-gutter-md q-mb-lg">
      <div class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="bg-white q-pa-md">
          <div class="row items-center justify-between">
            <div>
              <div class="text-caption text-grey-7 text-uppercase text-weight-medium">Total Users</div>
              <div class="text-h5 text-weight-bolder text-primary q-mt-xs">{{ metrics.users }}</div>
            </div>
            <q-avatar color="blue-1" text-color="primary" icon="group" size="48px" />
          </div>
        </q-card>
      </div>

      <div class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="bg-white q-pa-md">
          <div class="row items-center justify-between">
            <div>
              <div class="text-caption text-grey-7 text-uppercase text-weight-medium">Active Accounts</div>
              <div class="text-h5 text-weight-bolder text-positive q-mt-xs">{{ metrics.accounts }}</div>
            </div>
            <q-avatar color="green-1" text-color="positive" icon="badge" size="48px" />
          </div>
        </q-card>
      </div>

      <div class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="bg-white q-pa-md">
          <div class="row items-center justify-between">
            <div>
              <div class="text-caption text-grey-7 text-uppercase text-weight-medium">Connected Banks</div>
              <div class="text-h5 text-weight-bolder text-indigo q-mt-xs">{{ metrics.banks }}</div>
            </div>
            <q-avatar color="indigo-1" text-color="indigo" icon="apartment" size="48px" />
          </div>
        </q-card>
      </div>

      <div class="col-12 col-sm-6 col-md-3">
        <q-card flat bordered class="bg-white q-pa-md">
          <div class="row items-center justify-between">
            <div>
              <div class="text-caption text-grey-7 text-uppercase text-weight-medium">System Roles</div>
              <div class="text-h5 text-weight-bolder text-deep-purple q-mt-xs">{{ metrics.roles }}</div>
            </div>
            <q-avatar color="deep-purple-1" text-color="deep-purple" icon="verified_user" size="48px" />
          </div>
        </q-card>
      </div>
    </div>

    <!-- Quick Navigation Grid -->
    <div class="text-subtitle1 text-weight-bold text-grey-9 q-mb-md">Quick Navigation</div>
    <div class="row q-col-gutter-md">
      <div
        v-for="item in quickNav"
        :key="item.title"
        class="col-12 col-sm-6 col-md-4"
      >
        <q-card
          flat
          bordered
          clickable
          v-ripple
          class="bg-white cursor-pointer hover-card q-pa-md"
          @click="$router.push(item.to)"
        >
          <div class="row items-center">
            <q-avatar :color="item.colorBg" :text-color="item.colorText" :icon="item.icon" size="42px" class="q-mr-md" />
            <div>
              <div class="text-subtitle2 text-weight-bold text-grey-9">{{ item.title }}</div>
              <div class="text-caption text-grey-6">{{ item.desc }}</div>
            </div>
          </div>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'

const metrics = ref({
  users: 3,
  accounts: 2,
  banks: 3,
  roles: 4
})

const quickNav = [
  {
    title: 'Roles Management',
    desc: 'Configure system roles and permission sets',
    icon: 'verified_user',
    colorBg: 'blue-1',
    colorText: 'primary',
    to: '/admin/roles'
  },
  {
    title: 'Account Types',
    desc: 'Manage savings, checking, and deposit tiers',
    icon: 'account_balance',
    colorBg: 'green-1',
    colorText: 'positive',
    to: '/admin/account-types'
  },
  {
    title: 'Bank Accounts',
    desc: 'View customer accounts and balances',
    icon: 'badge',
    colorBg: 'amber-1',
    colorText: 'amber-9',
    to: '/admin/accounts'
  },
  {
    title: 'Deposits',
    desc: 'Process OTC and digital deposit transactions',
    icon: 'payments',
    colorBg: 'teal-1',
    colorText: 'teal-8',
    to: '/admin/deposits'
  },
  {
    title: 'Withdrawals',
    desc: 'Manage ATM and teller cash withdrawals',
    icon: 'remove_circle_outline',
    colorBg: 'red-1',
    colorText: 'negative',
    to: '/admin/withdrawals'
  },
  {
    title: 'Audit Logs',
    desc: 'Review security events and system activity',
    icon: 'history',
    colorBg: 'purple-1',
    colorText: 'purple',
    to: '/admin/audit-logs'
  }
]

async function refreshData() {
  try {
    const roles = await api.roles.list()
    const users = await api.users.list()
    const accounts = await api.accounts.list()
    const banks = await api.banks.list()

    metrics.value = {
      roles: roles?.length || 4,
      users: users?.length || 3,
      accounts: accounts?.length || 2,
      banks: banks?.length || 3
    }
  } catch (err) {
    console.error('Error refreshing metrics:', err)
  }
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.hover-card {
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.hover-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
</style>

