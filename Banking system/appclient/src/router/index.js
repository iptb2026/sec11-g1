import { defineRouter } from '#q-app'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router'

import routes from './routes.js'
import { useAuthStore } from '@/stores/auth-store'
import { CUSTOMERS_ONLY } from '@/utils/app-mode'

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default defineRouter((/* { store, ssrContext } */) => {
  const createHistory = import.meta.env.QUASAR_SERVER
    ? createMemoryHistory
    : (import.meta.env.QUASAR_VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(import.meta.env.QUASAR_VUE_ROUTER_BASE)
  })

  Router.beforeEach(async (to) => {
    const auth = useAuthStore()

    // Android app: customers only. A staff/admin/auditor still signed in from
    // before (e.g. an older version of the app) is signed out on the server too.
    if (CUSTOMERS_ONLY && auth.isAuthenticated && !auth.isCustomer) {
      await auth.logout()
      return to.path === '/login' ? true : '/login'
    }

    if (to.path === '/login' || to.path === '/signup') {
      // Already logged in? Skip the login and sign-up pages.
      return auth.isAuthenticated ? '/' : true
    }

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return '/login'
    }

    const allowedRoles = to.meta.roles
    if (allowedRoles && !allowedRoles.includes(auth.roleCode)) {
      return '/'
    }

    return true
  })

  return Router
})
