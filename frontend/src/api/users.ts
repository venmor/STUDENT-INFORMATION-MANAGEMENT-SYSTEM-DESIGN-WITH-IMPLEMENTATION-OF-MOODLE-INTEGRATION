import { api } from '@/api/axios'
import type { UserSummary } from '@/types'

export async function getUsers() {
  const response = await api.get<UserSummary[]>('/users')
  return response.data
}

export async function createUser(payload: {
  username: string
  email: string
  fullName: string
  primaryRole: string
  temporaryPassword: string
  capabilityNames?: string[]
}) {
  const response = await api.post<UserSummary>('/users', {
    username: payload.username,
    email: payload.email,
    full_name: payload.fullName,
    primary_role: payload.primaryRole,
    temporary_password: payload.temporaryPassword,
    capability_names: payload.capabilityNames ?? [],
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
  const response = await api.patch<UserSummary>(`/users/${userId}`, {
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
  const response = await api.post(`/users/${userId}/deactivate`)
  return response.data
}

export async function resetUserPassword(userId: number, newPassword: string) {
  const response = await api.post(`/users/${userId}/reset-password`, {
    new_password: newPassword,
  })
  return response.data
}

export async function changePassword(payload: { currentPassword: string; newPassword: string }) {
  const response = await api.post('/users/change-password', {
    current_password: payload.currentPassword,
    new_password: payload.newPassword,
  })
  return response.data
}
