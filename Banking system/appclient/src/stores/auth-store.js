import { defineStore } from 'pinia'
import api from '@/services/api'

const STORAGE_KEY = 'bank_auth'

function loadPersisted () {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

const persisted = loadPersisted()

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: persisted?.token || null,
    userId: persisted?.userId || null,
    username: persisted?.username || null,
    firstName: persisted?.firstName || null,
    lastName: persisted?.lastName || null,
    roleId: persisted?.roleId || null,
    roleCode: persisted?.roleCode || null,
    roleName: persisted?.roleName || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    fullName: (state) => [state.firstName, state.lastName].filter(Boolean).join(' '),
    isAdmin: (state) => state.roleCode === 'ADMIN',
    isStaff: (state) => state.roleCode === 'STAFF',
    isCustomer: (state) => state.roleCode === 'CUSTOMER',
    isAuditor: (state) => state.roleCode === 'AUDITOR',
  },

  actions: {
    persist () {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        token: this.token,
        userId: this.userId,
        username: this.username,
        firstName: this.firstName,
        lastName: this.lastName,
        roleId: this.roleId,
        roleCode: this.roleCode,
        roleName: this.roleName,
      }))
    },

    async login (username, password) {
      const form = new URLSearchParams()
      form.append('username', username)
      form.append('password', password)

      const { data } = await api.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      this.token = data.access_token

      // GET /auth/me returns the logged-in user and their role. (Customers
      // can't read the full user or role lists, so don't fetch those here.)
      const { data: me } = await api.get('/auth/me')

      this.userId = me.id
      this.username = me.username
      this.firstName = me.first_name
      this.lastName = me.last_name
      this.roleId = me.role_id
      this.roleCode = me.role_code
      this.roleName = me.role_name

      this.persist()
    },

    // Ends the session on the server too (revokes the token in `sessions`),
    // then forgets it locally. A failed call still logs out of the browser.
    async logout () {
      if (this.token) {
        try {
          await api.post('/auth/logout')
        } catch {
          // Token already expired or revoked: nothing left to end on the server.
        }
      }
      this.clearSession()
    },

    // Local-only logout, used when the server already rejected the token (401).
    clearSession () {
      this.token = null
      this.userId = null
      this.username = null
      this.firstName = null
      this.lastName = null
      this.roleId = null
      this.roleCode = null
      this.roleName = null
      localStorage.removeItem(STORAGE_KEY)
    },
  },
})
