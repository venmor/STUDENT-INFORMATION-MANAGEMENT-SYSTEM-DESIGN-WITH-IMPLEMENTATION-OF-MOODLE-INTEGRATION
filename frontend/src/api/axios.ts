import axios from 'axios'

import { useAuthStore } from '@/stores/authStore'
import type { RefreshResponse } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export const bareClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: 'application/json',
  },
})

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: 'application/json',
  },
})

let refreshPromise: Promise<string> | null = null

api.interceptors.request.use((config) => {
  const session = useAuthStore.getState().session
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const request = error.config as
      | (typeof error.config & { _retry?: boolean; skipAuthRefresh?: boolean })
      | undefined

    if (!request || request._retry || request.skipAuthRefresh || error.response?.status !== 401) {
      return Promise.reject(error)
    }

    const state = useAuthStore.getState()
    if (!state.session?.refreshToken) {
      state.logout()
      return Promise.reject(error)
    }

    request._retry = true

    if (!refreshPromise) {
      refreshPromise = bareClient
        .post<RefreshResponse>('/auth/refresh', { refresh_token: state.session.refreshToken })
        .then((response) => {
          state.refreshSession(response.data)
          const currentSession = useAuthStore.getState().session
          if (!currentSession) {
            throw new Error('Session refresh failed.')
          }
          return currentSession.accessToken
        })
        .catch((refreshError) => {
          state.logout()
          throw refreshError
        })
        .finally(() => {
          refreshPromise = null
        })
    }

    const accessToken = await refreshPromise
    request.headers = request.headers ?? {}
    request.headers.Authorization = `Bearer ${accessToken}`
    return api(request)
  },
)
