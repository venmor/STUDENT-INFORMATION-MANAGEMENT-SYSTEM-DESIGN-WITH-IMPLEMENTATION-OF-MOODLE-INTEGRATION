import type {
  Course,
  CourseSection,
  Enrollment,
  GradeRecord,
  SectionRosterEntry,
} from '@/api/contracts'
import { apiClient } from '@/api/http'

export async function getCourses() {
  const response = await apiClient.get<Course[]>('/courses')
  return response.data
}

export async function getSections() {
  const response = await apiClient.get<CourseSection[]>('/sections')
  return response.data
}

export async function getSection(sectionId: string) {
  const response = await apiClient.get<CourseSection>(`/sections/${sectionId}`)
  return response.data
}

export async function getSectionRoster(sectionId: string) {
  const response = await apiClient.get<SectionRosterEntry[]>(`/sections/${sectionId}/roster`)
  return response.data
}

export async function getEnrollments(filters?: {
  studentId?: string
  sectionId?: string
  includeInactive?: boolean
}) {
  const response = await apiClient.get<Enrollment[]>('/enrollments', {
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
  const response = await apiClient.post<Enrollment>('/enrollments', {
    section_id: payload.sectionId,
    student_user_id: payload.studentUserId,
    waitlist_if_full: payload.waitlistIfFull ?? false,
  })
  return response.data
}

export async function dropEnrollment(enrollmentId: string, reason?: string) {
  const response = await apiClient.post<Enrollment>(`/enrollments/${enrollmentId}/drop`, {
    reason,
  })
  return response.data
}

export async function getGrades(filters?: { studentId?: string }) {
  const response = await apiClient.get<GradeRecord[]>('/grades', {
    params: {
      student_id: filters?.studentId,
    },
  })
  return response.data
}

export async function createGrade(payload: {
  studentUserId: number
  sectionId: string
  numericScore?: string
  specialCode?: string
}) {
  const response = await apiClient.post<GradeRecord>('/grades', {
    student_user_id: payload.studentUserId,
    section_id: payload.sectionId,
    numeric_score: payload.numericScore,
    special_code: payload.specialCode ?? '',
  })
  return response.data
}

export async function updateGrade(
  gradeId: string,
  payload: { numericScore?: string; specialCode?: string; changeReason?: string },
) {
  const response = await apiClient.patch<GradeRecord>(`/grades/${gradeId}`, {
    numeric_score: payload.numericScore,
    special_code: payload.specialCode ?? '',
    change_reason: payload.changeReason ?? '',
  })
  return response.data
}

export async function officialiseGrade(gradeId: string) {
  const response = await apiClient.post<GradeRecord>(`/grades/${gradeId}/officialise`)
  return response.data
}
