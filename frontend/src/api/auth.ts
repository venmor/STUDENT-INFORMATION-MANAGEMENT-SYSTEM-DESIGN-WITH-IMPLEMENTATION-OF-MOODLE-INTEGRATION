import type { LoginPayload, LoginResponse } from '@/api/contracts'
import { bareClient, apiClient } from '@/api/http'
import type { Session } from '@/auth/auth-storage'

export async function login(credentials: LoginPayload) {
  const response = await bareClient.post<LoginResponse>('/auth/login', credentials)
  return mapLoginToSession(response.data)
}

export async function changePassword(payload: {
  currentPassword: string
  newPassword: string
}) {
  const response = await apiClient.post<{ detail: string }>('/users/change-password', {
    current_password: payload.currentPassword,
    new_password: payload.newPassword,
  })
  return response.data
}

export async function getAdvisorProbe() {
  const response = await apiClient.get<{ detail: string }>('/auth/probes/advisor')
  return response.data
}

function mapLoginToSession(data: LoginResponse): Session {
  return {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
    expiresAt: Date.now() + data.expires_in * 1000,
    user: {
      id: data.user.id,
      username: data.user.username,
      fullName: data.user.full_name,
      primaryRole: data.user.primary_role,
      mustResetPassword: data.user.must_reset_password,
      studentProfileId: data.user.student_profile_id,
    },
  }
}
