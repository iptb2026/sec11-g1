import { useAuthStore } from '@/stores/auth-store'

// AUDITOR can open the admin and operations pages but may only read them
// (the backend answers 403 to any write). Pages hide New/Edit/Delete when false.
export function useCanWrite () {
  return !useAuthStore().isAuditor
}
