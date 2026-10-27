const routes = [
  {
    path: '/login',
    component: () => import('@/pages/LoginPage.vue'),
  },
  {
    // Public customer sign-up (POST /auth/register)
    path: '/signup',
    component: () => import('@/pages/SignUpPage.vue'),
  },

  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: () => import('@/pages/DashboardPage.vue') },
      { path: 'profile', component: () => import('@/pages/ProfilePage.vue'), meta: { roles: ['ADMIN', 'STAFF', 'CUSTOMER', 'AUDITOR'] } },

      // --- ADMIN: system configuration ---
      { path: 'admin/roles', component: () => import('@/pages/admin/RolesPage.vue'), meta: { roles: ['ADMIN', 'AUDITOR'] } },
      { path: 'admin/account-types', component: () => import('@/pages/admin/AccountTypesPage.vue'), meta: { roles: ['ADMIN', 'AUDITOR'] } },
      { path: 'admin/banks', component: () => import('@/pages/admin/BanksPage.vue'), meta: { roles: ['ADMIN', 'AUDITOR'] } },
      { path: 'admin/fee-types', component: () => import('@/pages/admin/FeeTypesPage.vue'), meta: { roles: ['ADMIN', 'AUDITOR'] } },
      { path: 'admin/users', component: () => import('@/pages/admin/UsersPage.vue'), meta: { roles: ['ADMIN', 'AUDITOR'] } },
      { path: 'admin/audit-logs', component: () => import('@/pages/admin/AuditLogsPage.vue'), meta: { roles: ['ADMIN', 'AUDITOR'] } },

      // --- ADMIN + STAFF: day-to-day banking operations ---
      { path: 'accounts', component: () => import('@/pages/staff/AccountsPage.vue'), meta: { roles: ['ADMIN', 'STAFF', 'AUDITOR'] } },
      { path: 'withdrawal-limits', component: () => import('@/pages/staff/WithdrawalLimitsPage.vue'), meta: { roles: ['ADMIN', 'STAFF', 'AUDITOR'] } },
      { path: 'interest-policies', component: () => import('@/pages/staff/InterestPoliciesPage.vue'), meta: { roles: ['ADMIN', 'STAFF', 'AUDITOR'] } },
      { path: 'deposits', component: () => import('@/pages/staff/DepositsPage.vue'), meta: { roles: ['ADMIN', 'STAFF', 'AUDITOR'] } },
      { path: 'withdrawals', component: () => import('@/pages/staff/WithdrawalsPage.vue'), meta: { roles: ['ADMIN', 'STAFF', 'AUDITOR'] } },
      { path: 'transfers', component: () => import('@/pages/staff/TransfersPage.vue'), meta: { roles: ['ADMIN', 'STAFF', 'AUDITOR'] } },
      { path: 'interbank-transfers', component: () => import('@/pages/staff/InterbankTransfersPage.vue'), meta: { roles: ['ADMIN', 'STAFF', 'AUDITOR'] } },
      { path: 'fee-records', component: () => import('@/pages/staff/FeeRecordsPage.vue'), meta: { roles: ['ADMIN', 'STAFF', 'AUDITOR'] } },
      { path: 'interest-records', component: () => import('@/pages/staff/InterestRecordsPage.vue'), meta: { roles: ['ADMIN', 'STAFF', 'AUDITOR'] } },
      { path: 'ledger-entries', component: () => import('@/pages/staff/LedgerEntriesPage.vue'), meta: { roles: ['ADMIN', 'STAFF', 'AUDITOR'] } },

      // --- CUSTOMER: self-service ---
      { path: 'my-account', component: () => import('@/pages/customer/MyAccountPage.vue'), meta: { roles: ['CUSTOMER'] } },
      { path: 'my-transactions', component: () => import('@/pages/customer/MyTransactionsPage.vue'), meta: { roles: ['CUSTOMER'] } },
      { path: 'send-money', component: () => import('@/pages/customer/SendMoneyPage.vue'), meta: { roles: ['CUSTOMER'] } },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('@/pages/ErrorNotFound.vue'),
  }
]

export default routes
