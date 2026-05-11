import { api } from '@/api/axios'
import type {
  AdvisingNote,
  FinancialFlag,
  StudentCorrectionRequest,
  StudentProfile,
} from '@/types'

export async function getStudents() {
  const response = await api.get<StudentProfile[]>('/students')
  return response.data
}

export async function getStudent(studentId: string) {
  const response = await api.get<StudentProfile>(`/students/${studentId}`)
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
  const response = await api.patch<StudentProfile>(`/students/${studentId}`, {
    academic_standing: payload.academicStanding,
    standing_override_reason: payload.standingOverrideReason,
    year_of_study: payload.yearOfStudy,
    programme: payload.programme,
  })
  return response.data
}

export async function getFinancialFlags(studentId: string) {
  const response = await api.get<FinancialFlag[]>(`/students/${studentId}/financial-flags`)
  return response.data
}

export async function createFinancialFlag(
  studentId: string,
  payload: { flagType: string; reason: string; effectiveDate: string },
) {
  const response = await api.post<FinancialFlag>(`/students/${studentId}/financial-flags`, {
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
  const response = await api.patch<FinancialFlag>(
    `/students/${studentId}/financial-flags/${flagId}`,
    {
      reason: payload.reason,
      cleared_date: payload.clearedDate,
    },
  )
  return response.data
}

export async function getAdvisingNotes(studentId: string) {
  const response = await api.get<AdvisingNote[]>(`/students/${studentId}/advising-notes`)
  return response.data
}

export async function createAdvisingNote(studentId: string, noteText: string) {
  const response = await api.post<AdvisingNote>(`/students/${studentId}/advising-notes`, {
    note_text: noteText,
  })
  return response.data
}

export async function updateAdvisingNote(studentId: string, noteId: string, noteText: string) {
  const response = await api.patch<AdvisingNote>(`/students/${studentId}/advising-notes/${noteId}`, {
    note_text: noteText,
  })
  return response.data
}

export async function approveAdvisingNote(studentId: string, noteId: string) {
  const response = await api.post<AdvisingNote>(`/students/${studentId}/advising-notes/${noteId}/approve`)
  return response.data
}

export async function getCorrectionRequests(studentId: string) {
  const response = await api.get<StudentCorrectionRequest[]>(`/students/${studentId}/correction-requests`)
  return response.data
}

export async function createCorrectionRequest(
  studentId: string,
  payload: { requestedChanges: string; justification: string },
) {
  const response = await api.post<StudentCorrectionRequest>(
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
  const response = await api.patch<StudentCorrectionRequest>(
    `/students/${studentId}/correction-requests/${correctionRequestId}`,
    {
      status: payload.status,
      review_note: payload.reviewNote,
    },
  )
  return response.data
}

export async function downloadTranscript(studentId: string) {
  const response = await api.get<Blob>(`/students/${studentId}/transcript`, {
    responseType: 'blob',
  })
  return response.data
}
