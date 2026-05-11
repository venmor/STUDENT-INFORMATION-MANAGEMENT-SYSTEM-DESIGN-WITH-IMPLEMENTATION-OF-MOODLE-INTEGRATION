import { api } from '@/api/axios'
import type { GradeRecord } from '@/types'

export async function getGrades(filters?: { studentId?: string }) {
  const response = await api.get<GradeRecord[]>('/grades', {
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
  const response = await api.post<GradeRecord>('/grades', {
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
  const response = await api.patch<GradeRecord>(`/grades/${gradeId}`, {
    numeric_score: payload.numericScore,
    special_code: payload.specialCode ?? '',
    change_reason: payload.changeReason ?? '',
  })
  return response.data
}

export async function officialiseGrade(gradeId: string) {
  const response = await api.post<GradeRecord>(`/grades/${gradeId}/officialise`)
  return response.data
}
