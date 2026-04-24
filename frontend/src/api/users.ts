import type { UserSummary } from '@/api/contracts'
import { apiClient } from '@/api/http'

export async function getUsers() {
  const response = await apiClient.get<UserSummary[]>('/users')
  return response.data
}

export async function createUser(payload: {
  username: string
  email: string
  fullName: string
  primaryRole: string
  temporaryPassword: string
  capabilityNames: string[]
}) {
  const response = await apiClient.post<UserSummary>('/users', {
    username: payload.username,
    email: payload.email,
    full_name: payload.fullName,
    primary_role: payload.primaryRole,
    temporary_password: payload.temporaryPassword,
    capability_names: payload.capabilityNames,
  })
  return response.data
}

export async function updateUser(
  userId: number,
  payload: Partial<{
    email: string
    fullName: string
    primaryRole: string
    isActive: boolean
    mustResetPassword: boolean
    capabilityNames: string[]
  }>,
) {
  const response = await apiClient.patch<UserSummary>(`/users/${userId}`, {
    email: payload.email,
    full_name: payload.fullName,
    primary_role: payload.primaryRole,
    is_active: payload.isActive,
    must_reset_password: payload.mustResetPassword,
    capability_names: payload.capabilityNames,
  })
  return response.data
}

export async function deactivateUser(userId: number) {
  const response = await apiClient.post<{ detail: string }>(`/users/${userId}/deactivate`)
  return response.data
}

export async function resetUserPassword(userId: number, newPassword: string) {
  const response = await apiClient.post<{ detail: string }>(`/users/${userId}/reset-password`, {
    new_password: newPassword,
  })
  return response.data
}
