import axios from 'axios'

import type { RefreshResponse } from '@/api/contracts'
import { clearSession, loadStoredSession, persistSession } from '@/auth/auth-storage'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export const bareClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: 'application/json',
  },
})

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: 'application/json',
  },
})

let refreshPromise: Promise<string> | null = null

apiClient.interceptors.request.use((config) => {
  const session = loadStoredSession()
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config as
      | (typeof error.config & { _retry?: boolean; skipAuthRefresh?: boolean })
      | undefined

    if (
      !request ||
      request._retry ||
      request.skipAuthRefresh ||
      error.response?.status !== 401
    ) {
      return Promise.reject(error)
    }

    const session = loadStoredSession()
    if (!session?.refreshToken) {
      clearSession()
      return Promise.reject(error)
    }

    request._retry = true

    if (!refreshPromise) {
      refreshPromise = bareClient
        .post<RefreshResponse>('/auth/refresh', {
          refresh_token: session.refreshToken,
        })
        .then((response) => {
          const refreshedSession = {
            ...session,
            accessToken: response.data.access_token,
            refreshToken: response.data.refresh_token,
            expiresAt: Date.now() + response.data.expires_in * 1000,
          }
          persistSession(refreshedSession)
          return refreshedSession.accessToken
        })
        .catch((refreshError) => {
          clearSession()
          throw refreshError
        })
        .finally(() => {
          refreshPromise = null
        })
    }

    const accessToken = await refreshPromise
    request.headers.Authorization = `Bearer ${accessToken}`
    return apiClient(request)
  },
)
