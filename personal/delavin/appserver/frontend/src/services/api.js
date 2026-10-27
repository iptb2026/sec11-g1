// API Client Service for Mini Banking System
// ============================================================
// IMPORTANT: Replace the IP below with YOUR LAPTOP's local IP.
// Find it by running: ipconfig (Windows) → look for IPv4 Address
// Example: 192.168.1.175  →  http://192.168.1.175:5000
// ============================================================
const LAPTOP_IP = '192.168.1.175'
const BACKEND_PORT = 5000

export function getApiBaseUrl() {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }

  if (typeof window === 'undefined') {
    return `http://localhost:${BACKEND_PORT}`
  }

  // Detect Capacitor Android/iOS native app or webview
  const isCapacitor = Boolean(
    window.Capacitor?.isNativePlatform?.() ||
    window.Capacitor !== undefined ||
    window.location.protocol === 'capacitor:' ||
    window.location.protocol === 'ionic:' ||
    (navigator.userAgent && navigator.userAgent.includes('wv'))
  )

  if (isCapacitor) {
    return `http://${LAPTOP_IP}:${BACKEND_PORT}`
  }

  // If accessed in browser via local IP (e.g. http://192.168.1.175:9000)
  const hostname = window.location.hostname
  if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return `http://${hostname}:${BACKEND_PORT}`
  }

  return `http://localhost:${BACKEND_PORT}`
}

async function request(endpoint, options = {}) {
  const baseUrl = getApiBaseUrl()
  const url = `${baseUrl}${endpoint}`
  const defaultHeaders = {
    'Content-Type': 'application/json',
    Accept: 'application/json'
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(
        errorData.detail || `Request failed with status ${response.status}`
      )
    }

    if (response.status === 204) {
      return null
    }

    return await response.json()
  } catch (err) {
    console.warn(`API Error (${endpoint}):`, err.message)
    throw err
  }
}

export const api = {
  // Roles API
  roles: {
    list: () => request('/roles/'),
    get: (id) => request(`/roles/${id}`),
    create: (data) =>
      request('/roles/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),
    update: (id, data) =>
      request(`/roles/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      }),
    delete: (id) =>
      request(`/roles/${id}`, {
        method: 'DELETE'
      })
  },

  // Account Types API
  accountTypes: {
    list: () => request('/account-types/'),
    get: (id) => request(`/account-types/${id}`),
    create: (data) =>
      request('/account-types/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),
    update: (id, data) =>
      request(`/account-types/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      }),
    delete: (id) =>
      request(`/account-types/${id}`, {
        method: 'DELETE'
      })
  },

  // Banks API
  banks: {
    list: () => request('/banks/'),
    get: (id) => request(`/banks/${id}`),
    create: (data) =>
      request('/banks/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),
    update: (id, data) =>
      request(`/banks/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      }),
    delete: (id) =>
      request(`/banks/${id}`, {
        method: 'DELETE'
      })
  },

  // Fee Types API
  feeTypes: {
    list: () => request('/fee-types/'),
    get: (id) => request(`/fee-types/${id}`),
    create: (data) =>
      request('/fee-types/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),
    update: (id, data) =>
      request(`/fee-types/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      }),
    delete: (id) =>
      request(`/fee-types/${id}`, {
        method: 'DELETE'
      })
  },

  // Users API
  users: {
    list: () => request('/users/'),
    get: (id) => request(`/users/${id}`),
    create: (data) =>
      request('/users/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),
    update: (id, data) =>
      request(`/users/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      }),
    delete: (id) =>
      request(`/users/${id}`, {
        method: 'DELETE'
      })
  },

  // Audit Logs API
  auditLogs: {
    list: () => request('/audit-logs/')
  },

  // Accounts API
  accounts: {
    list: () => request('/accounts/'),
    get: (id) => request(`/accounts/${id}`),
    create: (data) =>
      request('/accounts/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),
    update: (id, data) =>
      request(`/accounts/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      }),
    delete: (id) =>
      request(`/accounts/${id}`, {
        method: 'DELETE'
      })
  },

  // Deposits API
  deposits: {
    list: () => request('/deposits/'),
    create: (data) =>
      request('/deposits/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  // Withdrawals API
  withdrawals: {
    list: () => request('/withdrawals/'),
    create: (data) =>
      request('/withdrawals/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  // Transfers API
  transfers: {
    list: () => request('/transfers/'),
    create: (data) =>
      request('/transfers/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  // Interbank Transfers API
  interbankTransfers: {
    list: () => request('/interbank-transfers/'),
    create: (data) =>
      request('/interbank-transfers/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  // Fee Records API
  feeRecords: {
    list: () => request('/fee-records/')
  },

  // Interest Records API
  interestRecords: {
    list: () => request('/interest-records/')
  },

  // Withdrawal Limits API
  withdrawalLimits: {
    list: () => request('/withdrawal-limits/'),
    create: (data) =>
      request('/withdrawal-limits/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  // Interest Policies API
  interestPolicies: {
    list: () => request('/interest-policies/'),
    create: (data) =>
      request('/interest-policies/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  }
}

export default api
