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

export async function downloadExamSlip(studentId: string, semester: string, academicYear: string) {
  const response = await api.get<Blob>(`/students/${studentId}/exam-slip`, {
    params: { semester, academic_year: academicYear },
    responseType: 'blob',
  })
  return response.data
}

export async function downloadResultsSlip(studentId: string, semester: string, academicYear: string) {
  const response = await api.get<Blob>(`/students/${studentId}/results-slip`, {
    params: { semester, academic_year: academicYear },
    responseType: 'blob',
  })
  return response.data
}

export async function downloadGradeTemplate(sectionId: string) {
  const response = await api.get<Blob>(`/sections/${sectionId}/grade-template`, {
    responseType: 'blob',
  })
  return response.data
}

export async function uploadGradePreview(sectionId: string, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post<{
    preview_rows: Array<{
      row_number: number
      student_id: string
      student_number: string
      ca_score: string | null
      exam_score: string | null
      total: string | null
    }>
    error_count: number
    errors: Array<{ row_number: number; detail: string }>
  }>(`/sections/${sectionId}/grade-upload-preview`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function uploadGradeCommit(sectionId: string, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post<{
    created_count: number
    error_count: number
    errors: Array<{ row_number: number; detail: string }>
  }>(`/sections/${sectionId}/grade-upload-commit`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}
