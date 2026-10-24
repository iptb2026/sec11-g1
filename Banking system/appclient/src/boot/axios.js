import { defineBoot } from '#q-app'
import { Notify } from 'quasar'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth-store'

export default defineBoot(({ app, router }) => {
  api.interceptors.request.use((config) => {
    const auth = useAuthStore()
    if (auth.token) {
      config.headers.Authorization = `Bearer ${auth.token}`
    }
    return config
  })

  api.interceptors.response.use(
    (response) => response,
    (error) => {
      const auth = useAuthStore()
      // A 401 while logged in means the session ended (expired, logged out
      // elsewhere, or the account was deactivated). A wrong password on the
      // login page is also a 401, but there is no token yet, so skip that.
      if (error.response && error.response.status === 401 && auth.token) {
        auth.clearSession()
        Notify.create({ type: 'warning', message: 'Your session expired, please log in again' })
        router.push('/login')
      }
      return Promise.reject(error)
    }
  )

  app.config.globalProperties.$api = api
})

export { api }
