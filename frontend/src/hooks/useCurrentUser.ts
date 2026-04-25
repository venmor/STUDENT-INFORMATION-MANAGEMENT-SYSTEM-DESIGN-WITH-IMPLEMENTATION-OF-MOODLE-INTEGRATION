import { useAuthStore } from '@/stores/authStore'

export function useCurrentUser() {
  return useAuthStore((state) => state.session?.user ?? null)
}
