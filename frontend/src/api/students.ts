import type {
  AdvisingNote,
  FinancialFlag,
  StudentCorrectionRequest,
  StudentProfile,
} from '@/api/contracts'
import { apiClient } from '@/api/http'

export async function getStudents() {
  const response = await apiClient.get<StudentProfile[]>('/students')
  return response.data
}

export async function getStudent(studentId: string) {
  const response = await apiClient.get<StudentProfile>(`/students/${studentId}`)
  return response.data
}

export async function updateStudent(
  studentId: string,
  payload: Partial<{
    academicStanding: string
    standingOverrideReason: string
    yearOfStudy: number
    programme: string
  }>,
) {
  const response = await apiClient.patch<StudentProfile>(`/students/${studentId}`, {
    academic_standing: payload.academicStanding,
    standing_override_reason: payload.standingOverrideReason,
    year_of_study: payload.yearOfStudy,
    programme: payload.programme,
  })
  return response.data
}

export async function getFinancialFlags(studentId: string) {
  const response = await apiClient.get<FinancialFlag[]>(`/students/${studentId}/financial-flags`)
  return response.data
}

export async function createFinancialFlag(
  studentId: string,
  payload: { flagType: string; reason: string; effectiveDate: string },
) {
  const response = await apiClient.post<FinancialFlag>(`/students/${studentId}/financial-flags`, {
    flag_type: payload.flagType,
    reason: payload.reason,
    effective_date: payload.effectiveDate,
  })
  return response.data
}

export async function updateFinancialFlag(
  studentId: string,
  flagId: string,
  payload: { reason?: string; clearedDate?: string | null },
) {
  const response = await apiClient.patch<FinancialFlag>(
    `/students/${studentId}/financial-flags/${flagId}`,
    {
      reason: payload.reason,
      cleared_date: payload.clearedDate,
    },
  )
  return response.data
}

export async function getAdvisingNotes(studentId: string) {
  const response = await apiClient.get<AdvisingNote[]>(`/students/${studentId}/advising-notes`)
  return response.data
}

export async function createAdvisingNote(studentId: string, noteText: string) {
  const response = await apiClient.post<AdvisingNote>(`/students/${studentId}/advising-notes`, {
    note_text: noteText,
  })
  return response.data
}

export async function updateAdvisingNote(studentId: string, noteId: string, noteText: string) {
  const response = await apiClient.patch<AdvisingNote>(
    `/students/${studentId}/advising-notes/${noteId}`,
    {
      note_text: noteText,
    },
  )
  return response.data
}

export async function approveAdvisingNote(studentId: string, noteId: string) {
  const response = await apiClient.post<AdvisingNote>(
    `/students/${studentId}/advising-notes/${noteId}/approve`,
  )
  return response.data
}

export async function getCorrectionRequests(studentId: string) {
  const response = await apiClient.get<StudentCorrectionRequest[]>(
    `/students/${studentId}/correction-requests`,
  )
  return response.data
}

export async function createCorrectionRequest(
  studentId: string,
  payload: { requestedChanges: string; justification: string },
) {
  const response = await apiClient.post<StudentCorrectionRequest>(
    `/students/${studentId}/correction-requests`,
    {
      requested_changes: payload.requestedChanges,
      justification: payload.justification,
    },
  )
  return response.data
}

export async function reviewCorrectionRequest(
  studentId: string,
  correctionRequestId: string,
  payload: { status: string; reviewNote: string },
) {
  const response = await apiClient.patch<StudentCorrectionRequest>(
    `/students/${studentId}/correction-requests/${correctionRequestId}`,
    {
      status: payload.status,
      review_note: payload.reviewNote,
    },
  )
  return response.data
}

export async function downloadTranscript(studentId: string) {
  const response = await apiClient.get<Blob>(`/students/${studentId}/transcript`, {
    responseType: 'blob',
  })
  return response.data
}
