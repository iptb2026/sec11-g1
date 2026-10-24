import { onMounted, onBeforeUnmount } from 'vue'
import { onDataChangedElsewhere } from '@/services/api'

/**
 * Keeps a page's listing up to date without reloading the whole page.
 *
 *   useAutoRefresh(refresh)
 *
 * - loads once when the page opens (with the loading spinner)
 * - reloads silently when another tab adds / edits / deletes something
 * - reloads silently when you switch back to this tab
 * - reloads silently every `interval` ms while the tab is visible,
 *   so changes made by other users show up too
 *
 * `refresh` receives `{ silent: true }` for background reloads so the page can
 * skip the loading spinner. The page itself still calls `await refresh()`
 * right after its own saves and deletes.
 */
export function useAutoRefresh (refresh, { interval = 15000 } = {}) {
  let timer = null
  let stopListening = null
  let running = false

  async function silentRefresh () {
    if (running || document.visibilityState !== 'visible') return
    running = true
    try {
      await refresh({ silent: true })
    } catch (err) {
      // Background reload failed (e.g. server briefly down) — try again next tick.
      console.warn('Auto-refresh failed', err)
    } finally {
      running = false
    }
  }

  function onVisibilityChange () {
    if (document.visibilityState === 'visible') silentRefresh()
  }

  onMounted(() => {
    refresh()
    stopListening = onDataChangedElsewhere(silentRefresh)
    document.addEventListener('visibilitychange', onVisibilityChange)
    timer = setInterval(silentRefresh, interval)
  })

  onBeforeUnmount(() => {
    clearInterval(timer)
    stopListening?.()
    document.removeEventListener('visibilitychange', onVisibilityChange)
  })
}
