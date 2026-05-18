import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'

import type { AuthSession, LoginResponse, RefreshResponse } from '@/types'

interface ImpersonationState {
  id: number
  username: string
  fullName: string
  primaryRole: string
  studentProfileId: string | null
}

interface AuthState {
  session: AuthSession | null
  impersonating: ImpersonationState | null
  setSession: (session: AuthSession) => void
  loginFromResponse: (payload: LoginResponse) => void
  refreshSession: (payload: RefreshResponse) => void
  startImpersonation: (target: ImpersonationState) => void
  stopImpersonation: () => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      session: null,
      impersonating: null,
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
              availableRoles: payload.user.available_roles || [payload.user.primary_role],
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
      startImpersonation: (target) => set({ impersonating: target }),
      stopImpersonation: () => set({ impersonating: null }),
      logout: () => set({ session: null, impersonating: null }),
    }),
    {
      name: 'sis-auth',
      storage: createJSONStorage(() => sessionStorage),
    },
  ),
)
