import { api } from '@/api/axios'
import type { Enrollment, SectionRosterEntry } from '@/types'

export async function getEnrollments(filters?: {
  studentId?: string
  sectionId?: string
  includeInactive?: boolean
}) {
  const response = await api.get<Enrollment[]>('/enrollments', {
    params: {
      student_id: filters?.studentId,
      section_id: filters?.sectionId,
      include_inactive: filters?.includeInactive,
    },
  })
  return response.data
}

export async function createEnrollment(payload: {
  sectionId: string
  studentUserId?: number
  waitlistIfFull?: boolean
}) {
  const response = await api.post<Enrollment>('/enrollments', {
    section_id: payload.sectionId,
    student_user_id: payload.studentUserId,
    waitlist_if_full: payload.waitlistIfFull ?? false,
  })
  return response.data
}

export async function dropEnrollment(enrollmentId: string, reason?: string) {
  const response = await api.post<Enrollment>(`/enrollments/${enrollmentId}/drop`, {
    reason,
  })
  return response.data
}

export async function getSectionRoster(sectionId: string) {
  const response = await api.get<SectionRosterEntry[]>(`/sections/${sectionId}/roster`)
  return response.data
}

export async function createPendingRegistration(payload: {
  sectionId: string
  studentUserId?: number
}) {
  const response = await api.post<Enrollment>('/registrations/pending/create', {
    section_id: payload.sectionId,
    student_user_id: payload.studentUserId,
  })
  return response.data
}

export async function getPendingRegistrations() {
  const response = await api.get<Enrollment[]>('/registrations/pending')
  return response.data
}

export async function approvePendingRegistration(enrollmentId: string) {
  const response = await api.post<Enrollment>(`/registrations/${enrollmentId}/approve`)
  return response.data
}

export async function rejectPendingRegistration(enrollmentId: string, reason?: string) {
  const response = await api.post<Enrollment>(`/registrations/${enrollmentId}/reject`, { reason })
  return response.data
}
