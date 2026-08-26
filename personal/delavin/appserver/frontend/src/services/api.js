// API Client Service for Mini Banking System
const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'http://localhost:5004'
    : '')

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
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

// Initial seed / fallback data
export const defaultRoles = [
  {
    id: 1,
    role_code: 'ADMIN',
    role_name: 'Admin',
    description: 'System Administrator',
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    role_code: 'STAFF',
    role_name: 'Staff',
    description: 'Bank staff user',
    created_at: new Date().toISOString()
  },
  {
    id: 3,
    role_code: 'CUSTOMER',
    role_name: 'Customer',
    description: 'Bank customer',
    created_at: new Date().toISOString()
  },
  {
    id: 4,
    role_code: 'AUDITOR',
    role_name: 'Auditor',
    description: 'Read-only compliance auditor',
    created_at: new Date().toISOString()
  }
]

export const defaultAccountTypes = [
  {
    id: 1,
    type_code: 'SAVINGS',
    type_name: 'Savings Account',
    minimum_balance: '500.00',
    opening_deposit: '1000.00',
    annual_interest_rate: '1.50',
    daily_withdrawal_limit: '50000.00',
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    type_code: 'CHECKING',
    type_name: 'Checking Account',
    minimum_balance: '1000.00',
    opening_deposit: '5000.00',
    annual_interest_rate: '0.25',
    daily_withdrawal_limit: '100000.00',
    created_at: new Date().toISOString()
  },
  {
    id: 3,
    type_code: 'TIME_DEPOSIT',
    type_name: 'Time Deposit Account',
    minimum_balance: '10000.00',
    opening_deposit: '10000.00',
    annual_interest_rate: '4.50',
    daily_withdrawal_limit: '0.00',
    created_at: new Date().toISOString()
  }
]

export const defaultBanks = [
  {
    id: 1,
    bank_code: 'BDO',
    swift_code: 'BNORPHMM',
    bank_name: 'Banco de Oro',
    short_name: 'BDO',
    api_endpoint: 'https://api.bdo.com.ph',
    contact_email: 'support@bdo.com.ph',
    status: 'ACTIVE'
  },
  {
    id: 2,
    bank_code: 'BPI',
    swift_code: 'BOPIPHMM',
    bank_name: 'Bank of the Philippine Islands',
    short_name: 'BPI',
    api_endpoint: 'https://api.bpi.com.ph',
    contact_email: 'support@bpi.com.ph',
    status: 'ACTIVE'
  },
  {
    id: 3,
    bank_code: 'MBTC',
    swift_code: 'MBTCPHMM',
    bank_name: 'Metrobank',
    short_name: 'Metrobank',
    api_endpoint: 'https://api.metrobank.com.ph',
    contact_email: 'support@metrobank.com.ph',
    status: 'ACTIVE'
  }
]

export const defaultFeeTypes = [
  {
    id: 1,
    fee_code: 'ATM_WITHDRAWAL',
    fee_name: 'Interbank ATM Withdrawal Fee',
    fee_type: 'FIXED',
    amount: '18.00',
    currency: 'PHP'
  },
  {
    id: 2,
    fee_code: 'INSTAPAY',
    fee_name: 'InstaPay Transfer Fee',
    fee_type: 'FIXED',
    amount: '25.00',
    currency: 'PHP'
  },
  {
    id: 3,
    fee_code: 'MAINTENANCE',
    fee_name: 'Below Minimum Balance Monthly Fee',
    fee_type: 'FIXED',
    amount: '300.00',
    currency: 'PHP'
  }
]

export const defaultUsers = [
  {
    id: 1,
    role_id: 1,
    role_name: 'Admin',
    username: 'admin',
    email: 'admin@minibank.com',
    first_name: 'System',
    last_name: 'Administrator',
    phone_number: '+639123456789',
    status: 'ACTIVE'
  },
  {
    id: 2,
    role_id: 2,
    role_name: 'Staff',
    username: 'teller1',
    email: 'teller1@minibank.com',
    first_name: 'Maria',
    last_name: 'Santos',
    phone_number: '+639234567890',
    status: 'ACTIVE'
  },
  {
    id: 3,
    role_id: 3,
    role_name: 'Customer',
    username: 'juandelacruz',
    email: 'juan@example.com',
    first_name: 'Juan',
    last_name: 'Dela Cruz',
    phone_number: '+639345678901',
    status: 'ACTIVE'
  }
]

export const defaultAccounts = [
  {
    id: 1,
    user_id: 3,
    account_number: '1001-2026-0001',
    account_type: 'Savings Account',
    account_type_id: 1,
    balance: '25450.00',
    currency: 'PHP',
    status: 'ACTIVE',
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    user_id: 3,
    account_number: '1001-2026-0002',
    account_type: 'Checking Account',
    account_type_id: 2,
    balance: '82100.50',
    currency: 'PHP',
    status: 'ACTIVE',
    created_at: new Date().toISOString()
  }
]

export const api = {
  // Roles API
  roles: {
    list: () => request('/roles/').catch(() => defaultRoles),
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
    list: () => request('/account-types/').catch(() => defaultAccountTypes),
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
    list: () => request('/banks/').catch(() => defaultBanks),
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
    list: () => request('/fee-types/').catch(() => defaultFeeTypes),
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
    list: () => request('/users/').catch(() => defaultUsers),
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
    list: () =>
      request('/audit-logs/').catch(() => [
        {
          id: 1,
          user_id: 1,
          action: 'LOGIN',
          details: 'Admin logged in successfully',
          ip_address: '127.0.0.1',
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          user_id: 1,
          action: 'CREATE_ROLE',
          details: 'Created role: AUDITOR',
          ip_address: '127.0.0.1',
          created_at: new Date().toISOString()
        }
      ])
  },

  // Accounts API
  accounts: {
    list: () => request('/accounts/').catch(() => defaultAccounts),
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
    list: () =>
      request('/deposits/').catch(() => [
        {
          id: 1,
          account_id: 1,
          amount: '5000.00',
          channel: 'OVER_THE_COUNTER',
          reference_number: 'DEP-2026-0001',
          created_at: new Date().toISOString()
        }
      ]),
    create: (data) =>
      request('/deposits/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  // Withdrawals API
  withdrawals: {
    list: () =>
      request('/withdrawals/').catch(() => [
        {
          id: 1,
          account_id: 1,
          amount: '1000.00',
          channel: 'ATM',
          reference_number: 'WDR-2026-0001',
          created_at: new Date().toISOString()
        }
      ]),
    create: (data) =>
      request('/withdrawals/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  // Transfers API
  transfers: {
    list: () =>
      request('/transfers/').catch(() => [
        {
          id: 1,
          source_account_id: 1,
          destination_account_id: 2,
          amount: '2000.00',
          status: 'COMPLETED',
          reference_number: 'TRF-2026-0001',
          created_at: new Date().toISOString()
        }
      ]),
    create: (data) =>
      request('/transfers/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  // Interbank Transfers API
  interbankTransfers: {
    list: () =>
      request('/interbank-transfers/').catch(() => [
        {
          id: 1,
          source_account_id: 1,
          target_bank_id: 2,
          target_account_number: '1234567890',
          amount: '1500.00',
          status: 'COMPLETED',
          reference_number: 'IBT-2026-0001',
          created_at: new Date().toISOString()
        }
      ]),
    create: (data) =>
      request('/interbank-transfers/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  // Fee Records API
  feeRecords: {
    list: () =>
      request('/fee-records/').catch(() => [
        {
          id: 1,
          account_id: 1,
          fee_type_id: 1,
          amount: '18.00',
          created_at: new Date().toISOString()
        }
      ])
  },

  // Interest Records API
  interestRecords: {
    list: () =>
      request('/interest-records/').catch(() => [
        {
          id: 1,
          account_id: 1,
          amount: '31.81',
          period_start: '2026-07-01',
          period_end: '2026-07-31',
          created_at: new Date().toISOString()
        }
      ])
  },

  // Withdrawal Limits API
  withdrawalLimits: {
    list: () =>
      request('/withdrawal-limits/').catch(() => [
        {
          id: 1,
          account_type_id: 1,
          daily_limit: '50000.00',
          monthly_limit: '500000.00',
          created_at: new Date().toISOString()
        }
      ]),
    create: (data) =>
      request('/withdrawal-limits/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  // Interest Policies API
  interestPolicies: {
    list: () =>
      request('/interest-policies/').catch(() => [
        {
          id: 1,
          account_type_id: 1,
          rate: '1.50',
          period: 'ANNUAL',
          created_at: new Date().toISOString()
        }
      ]),
    create: (data) =>
      request('/interest-policies/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  }
}

export default api

