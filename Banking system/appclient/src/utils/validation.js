// Reusable Quasar `:rules` validators. Each returns true or an error message.
const isEmpty = (val) => val === null || val === undefined || val === ''

export const required = (val) => !isEmpty(val) || 'Required'

export const positiveAmount = (val) => (!isEmpty(val) && Number(val) > 0) || 'Must be greater than 0'

export const nonNegative = (val) => isEmpty(val) || Number(val) >= 0 || 'Cannot be negative'

export const isDate = (val) => /^\d{4}-\d{2}-\d{2}$/.test(val || '') || 'Use YYYY-MM-DD'

export const optionalDate = (val) => isEmpty(val) || isDate(val)

export const optionalEmail = (val) => isEmpty(val) || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val) || 'Enter a valid email'

// Same minimum as the backend (MIN_PASSWORD_LENGTH in appserver/app/schemas/user.py).
export const PASSWORD_MIN = 8

export const password = (val) => (!isEmpty(val) && String(val).length >= PASSWORD_MIN) || `At least ${PASSWORD_MIN} characters`

// Blank = keep the current password (edit forms).
export const optionalPassword = (val) => isEmpty(val) || String(val).length >= PASSWORD_MIN || `At least ${PASSWORD_MIN} characters`
