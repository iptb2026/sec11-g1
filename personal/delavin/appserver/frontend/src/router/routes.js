const routes = [
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '', redirect: '/admin/roles' },
      { path: 'admin', redirect: '/admin/roles' },
      { path: 'admin/dashboard', component: () => import('@/pages/DashboardPage.vue') },
      { path: 'admin/roles', component: () => import('@/pages/RolesPage.vue') },
      { path: 'admin/account-types', component: () => import('@/pages/AccountTypesPage.vue') },
      { path: 'admin/banks', component: () => import('@/pages/BanksPage.vue') },
      { path: 'admin/fee-types', component: () => import('@/pages/FeeTypesPage.vue') },
      { path: 'admin/users', component: () => import('@/pages/UsersPage.vue') },
      { path: 'admin/audit-logs', component: () => import('@/pages/AuditLogsPage.vue') },
      { path: 'admin/accounts', component: () => import('@/pages/AccountsPage.vue') },
      { path: 'admin/withdrawal-limits', component: () => import('@/pages/WithdrawalLimitsPage.vue') },
      { path: 'admin/interest-policies', component: () => import('@/pages/InterestPoliciesPage.vue') },
      { path: 'admin/deposits', component: () => import('@/pages/DepositsPage.vue') },
      { path: 'admin/withdrawals', component: () => import('@/pages/WithdrawalsPage.vue') },
      { path: 'admin/transfers', component: () => import('@/pages/TransfersPage.vue') },
      { path: 'admin/interbank-transfers', component: () => import('@/pages/InterbankTransfersPage.vue') },
      { path: 'admin/fee-records', component: () => import('@/pages/FeeRecordsPage.vue') },
      { path: 'admin/interest-records', component: () => import('@/pages/InterestRecordsPage.vue') }
    ]
  },

  // Always leave this as last one
  {
    path: '/:catchAll(.*)*',
    component: () => import('@/pages/ErrorNotFound.vue')
  }
]

export default routes
