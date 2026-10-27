import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.QCLI_API_BASE_URL || 'http://127.0.0.1:8000',
})

// --- Cross-tab change notifications ---
// After any successful add / edit / delete, tell the app's OTHER open tabs that
// data changed so their listings reload (see composables/useAutoRefresh.js).
// The tab that made the change already reloads itself right after saving.
const channel = typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('mini-bank-data') : null

api.interceptors.response.use((response) => {
  if (['post', 'put', 'patch', 'delete'].includes(response.config.method)) {
    channel?.postMessage({ url: response.config.url, at: Date.now() })
  }
  return response
})

export function onDataChangedElsewhere (handler) {
  if (!channel) return () => {}
  const listener = () => handler()
  channel.addEventListener('message', listener)
  return () => channel.removeEventListener('message', listener)
}

// Turns a failed request into a readable message. FastAPI returns `detail`
// as a string for 400/404/409, but as a list of field errors for 422.
export function errorMessage (err, fallback = 'Request failed') {
  const detail = err.response?.data?.detail
  if (Array.isArray(detail)) {
    return detail.map((d) => `${d.loc?.slice(-1)[0] ?? ''}: ${d.msg}`).join('; ')
  }
  return detail || fallback
}

// Optional fields left empty in a form arrive as '' — the backend expects null
// (an empty string is not a valid email or date and fails with 422).
export function blankToNull (obj) {
  return Object.fromEntries(Object.entries(obj).map(([k, v]) => [k, v === '' ? null : v]))
}

export default api
