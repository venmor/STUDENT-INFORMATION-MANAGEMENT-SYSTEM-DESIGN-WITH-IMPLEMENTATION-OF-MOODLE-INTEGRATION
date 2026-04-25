import { bareClient } from '@/api/axios'
import type { LoginPayload, LoginResponse } from '@/types'

export async function login(payload: LoginPayload) {
  const response = await bareClient.post<LoginResponse>('/auth/login', payload)
  return response.data
}
