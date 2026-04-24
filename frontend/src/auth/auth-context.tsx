/* eslint-disable react-refresh/only-export-components */

import type { ReactNode } from 'react'
import { createContext, useContext, useEffect, useMemo, useState } from 'react'

import type { LoginPayload } from '@/api/contracts'
import { login } from '@/api/auth'
import {
  clearSession,
  loadStoredSession,
  persistSession,
  subscribeToSession,
  type Session,
} from '@/auth/auth-storage'

interface AuthContextValue {
  isAuthenticated: boolean
  session: Session | null
  loginUser: (credentials: LoginPayload) => Promise<Session>
  logoutUser: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({
  children,
  initialSession,
}: {
  children: ReactNode
  initialSession?: Session | null
}) {
  const [session, setSession] = useState<Session | null>(() => initialSession ?? loadStoredSession())

  useEffect(() => {
    return subscribeToSession(setSession)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      isAuthenticated: Boolean(session?.accessToken),
      session,
      async loginUser(credentials) {
        const nextSession = await login(credentials)
        persistSession(nextSession)
        return nextSession
      },
      logoutUser() {
        clearSession()
      },
    }),
    [session],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
