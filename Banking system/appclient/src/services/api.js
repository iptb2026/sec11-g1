import axios from 'axios'

// On a phone (or any other device) opening this PC's or server's address,
// 127.0.0.1 / localhost would mean the phone itself. So when the page was not
// opened on localhost, point a loopback API URL at the host the page came from.
// Opened on the PC itself, nothing changes.
function apiBaseUrl () {
  const url = new URL(import.meta.env.QCLI_API_BASE_URL || 'http://127.0.0.1:8000/catarig/')
  const loopback = ['127.0.0.1', 'localhost']
  if (loopback.includes(url.hostname) && !loopback.includes(window.location.hostname)) {
    url.hostname = window.location.hostname
  }
  return url.toString()
}

const api = axios.create({
  baseURL: apiBaseUrl(),
})

export default api
