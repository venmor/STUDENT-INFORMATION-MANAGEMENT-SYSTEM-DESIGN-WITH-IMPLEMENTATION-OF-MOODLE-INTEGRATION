import type { PrimaryRole } from '@/api/contracts'

const SESSION_STORAGE_KEY = 'modern-sis-session'

export interface SessionUser {
  id: number
  username: string
  fullName: string
  primaryRole: PrimaryRole
  mustResetPassword: boolean
  studentProfileId: string | null
}

export interface Session {
  accessToken: string
  refreshToken: string
  expiresAt: number
  user: SessionUser
}

type SessionListener = (session: Session | null) => void

const listeners = new Set<SessionListener>()

function emitSession(session: Session | null) {
  listeners.forEach((listener) => listener(session))
}

export function subscribeToSession(listener: SessionListener) {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

export function loadStoredSession() {
  const raw = window.sessionStorage.getItem(SESSION_STORAGE_KEY)
  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw) as Session
  } catch {
    window.sessionStorage.removeItem(SESSION_STORAGE_KEY)
    return null
  }
}

export function persistSession(session: Session) {
  window.sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session))
  emitSession(session)
}

export function clearSession() {
  window.sessionStorage.removeItem(SESSION_STORAGE_KEY)
  emitSession(null)
}
