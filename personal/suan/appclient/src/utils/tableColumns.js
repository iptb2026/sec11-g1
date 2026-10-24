// Shared column clean-up for every q-table, so tables fit the screen without
// sideways scrolling: readable dates and money, and no internal ID columns
// when the account number/name is already shown.

const DATE_ONLY = /^\d{4}-\d{2}-\d{2}$/
const DATE_FIELD = /(_date|_at|_timestamp)$/
const REFERENCE_FIELD = /reference/
const MONEY_FIELD = /^(amount|transfer_fee|fixed_amount|opening_deposit|minimum_balance|daily_withdrawal_limit|.*_balance|.*_amount|balance_before|balance_after)$/

// Internal id column -> the readable column that makes it redundant.
const REDUNDANT_IDS = {
  account_id: ['account_number'],
  source_account_id: ['from_account_number', 'source_account_number'],
  destination_account_id: ['to_account_number'],
}

export function formatMoney (val) {
  if (val === null || val === undefined || val === '') return '—'
  return '₱' + Number(val).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export function formatDate (val) {
  if (!val) return '—'
  const text = String(val)
  if (DATE_ONLY.test(text)) {
    return new Date(text + 'T00:00:00').toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
  }
  // The API sends UTC without a timezone; mark it as UTC so it shows in local time.
  const date = new Date(/[zZ]|[+-]\d{2}:?\d{2}$/.test(text) ? text : text + 'Z')
  if (Number.isNaN(date.getTime())) return text
  // Date and time on separate lines (the cell uses white-space: pre-line).
  const day = date.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
  const time = date.toLocaleTimeString('en-PH', { hour: 'numeric', minute: '2-digit' })
  return `${day}\n${time}`
}

export function tableColumns (columns) {
  const names = new Set(columns.map((c) => c.name))
  return columns
    .filter((col) => !(REDUNDANT_IDS[col.name] || []).some((readable) => names.has(readable)))
    .map((col) => {
      if (col.name === 'id') return { ...col, classes: 'bank-cell-id', headerClasses: 'bank-cell-id' }
      // Account numbers never split across lines.
      if (col.name.endsWith('account_number')) return { ...col, classes: 'bank-cell-ref' }
      if (col.format || typeof col.field !== 'string') return col
      if (DATE_FIELD.test(col.field)) {
        return { ...col, format: formatDate, classes: 'bank-cell-date', headerClasses: 'bank-cell-date' }
      }
      if (REFERENCE_FIELD.test(col.field)) {
        return { ...col, classes: 'bank-cell-ref' }
      }
      // Ledger style: a zero debit or credit is left blank.
      if (col.field === 'debit_amount' || col.field === 'credit_amount') {
        return { ...col, align: 'right', format: (v) => (Number(v) ? formatMoney(v) : '—'), classes: 'bank-cell-money' }
      }
      if (MONEY_FIELD.test(col.field)) {
        return { ...col, align: 'right', format: formatMoney, classes: 'bank-cell-money' }
      }
      return col
    })
}
