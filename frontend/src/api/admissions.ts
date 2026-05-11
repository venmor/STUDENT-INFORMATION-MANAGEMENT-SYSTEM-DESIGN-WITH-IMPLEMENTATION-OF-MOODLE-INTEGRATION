import { api } from '@/api/axios'
import type {
  ApplicantCreatePayload,
  ApplicantDocumentUploadPayload,
  ApplicantProfile,
} from '@/types/admissions'

const publicApi = api

export async function createApplication(payload: ApplicantCreatePayload) {
  const response = await publicApi.post<ApplicantProfile>('/admissions/apply', payload)
  return response.data
}

export async function uploadApplicantDocument(payload: ApplicantDocumentUploadPayload) {
  const formData = new FormData()
  formData.append('document_type', payload.documentType)
  formData.append('file', payload.file)
  const response = await publicApi.post<{ id: string }>(
    `/admissions/apply/${payload.applicantId}/documents`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return response.data
}

export async function submitApplication(applicantId: string) {
  const response = await publicApi.post<ApplicantProfile>(
    `/admissions/apply/${applicantId}/submit`,
  )
  return response.data
}

export async function getApplications(params?: { status?: string; programme?: string }) {
  const response = await api.get<ApplicantProfile[]>('/admissions/applications', { params })
  return response.data
}

export async function getApplication(applicantId: string) {
  const response = await api.get<ApplicantProfile>(`/admissions/applications/${applicantId}`)
  return response.data
}

export async function approveApplication(applicantId: string, reviewNotes?: string) {
  const response = await api.post<ApplicantProfile>(
    `/admissions/applications/${applicantId}/approve`,
    { review_notes: reviewNotes || '' },
  )
  return response.data
}

export async function rejectApplication(applicantId: string, reviewNotes?: string) {
  const response = await api.post<ApplicantProfile>(
    `/admissions/applications/${applicantId}/reject`,
    { review_notes: reviewNotes || '' },
  )
  return response.data
}
