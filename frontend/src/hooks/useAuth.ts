import { useNavigate } from 'react-router-dom'

import { login } from '@/api/auth'
import { useAuthStore } from '@/stores/authStore'

export function useAuth() {
  const navigate = useNavigate()
  const session = useAuthStore((state) => state.session)
  const loginFromResponse = useAuthStore((state) => state.loginFromResponse)
  const logoutStore = useAuthStore((state) => state.logout)

  return {
    session,
    async signIn(username: string, password: string) {
      const response = await login({ username, password })
      loginFromResponse(response)
      return response
    },
    logout() {
      logoutStore()
      navigate('/login')
    },
  }
}
