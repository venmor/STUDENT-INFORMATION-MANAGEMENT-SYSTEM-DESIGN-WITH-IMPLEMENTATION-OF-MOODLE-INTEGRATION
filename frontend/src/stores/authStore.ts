import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'

import type { AuthSession, LoginResponse, RefreshResponse } from '@/types'

interface AuthState {
  session: AuthSession | null
  setSession: (session: AuthSession) => void
  loginFromResponse: (payload: LoginResponse) => void
  refreshSession: (payload: RefreshResponse) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      session: null,
      setSession: (session) => set({ session }),
      loginFromResponse: (payload) =>
        set({
          session: {
            accessToken: payload.access_token,
            refreshToken: payload.refresh_token,
            expiresAt: Date.now() + payload.expires_in * 1000,
            user: {
              id: payload.user.id,
              username: payload.user.username,
              fullName: payload.user.full_name,
              primaryRole: payload.user.primary_role,
              mustResetPassword: payload.user.must_reset_password,
              studentProfileId: payload.user.student_profile_id,
            },
          },
        }),
      refreshSession: (payload) => {
        const current = get().session
        if (!current) {
          return
        }
        set({
          session: {
            ...current,
            accessToken: payload.access_token,
            refreshToken: payload.refresh_token,
            expiresAt: Date.now() + payload.expires_in * 1000,
          },
        })
      },
      logout: () => set({ session: null }),
    }),
    {
      name: 'sis-auth',
      storage: createJSONStorage(() => sessionStorage),
    },
  ),
)
