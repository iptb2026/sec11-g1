// The Android app (Quasar's Capacitor build) is for customers only, as the
// instructor asked: staff, admins and auditors use the web app. This is set at
// build time, so the web app is not affected.
export const CUSTOMERS_ONLY = import.meta.env.QUASAR_MODE === 'capacitor'

export const CUSTOMERS_ONLY_MESSAGE = 'This app is for customers. Staff, admins and auditors use the web app.'
