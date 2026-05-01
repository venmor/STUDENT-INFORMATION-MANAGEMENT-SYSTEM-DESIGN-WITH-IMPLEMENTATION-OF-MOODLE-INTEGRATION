import { api } from '@/api/axios'
import type {
  DocumentFilters,
  DocumentReport,
  DocumentSummary,
  ReviewDocumentPayload,
  StudentDocument,
  UploadDocumentPayload,
} from '@/types/documents'

function documentFilterParams(filters: DocumentFilters = {}) {
  return {
    student: filters.student || undefined,
    document_type: filters.documentType && filters.documentType !== 'ALL' ? filters.documentType : undefined,
    visibility: filters.visibility && filters.visibility !== 'ALL' ? filters.visibility : undefined,
    status: filters.status && filters.status !== 'ALL' ? filters.status : undefined,
    uploaded_by: filters.uploadedBy || undefined,
    search: filters.search || undefined,
    date_from: filters.dateFrom || undefined,
    date_to: filters.dateTo || undefined,
  }
}

function uploadFormData(payload: UploadDocumentPayload) {
  const formData = new FormData()
  if (payload.studentId) {
    formData.append('student', payload.studentId)
  }
  formData.append('documentType', payload.documentType)
  formData.append('title', payload.title)
  formData.append('description', payload.description)
  formData.append('visibility', payload.visibility)
  formData.append('file', payload.file)
  return formData
}

export async function getDocuments(filters: DocumentFilters = {}) {
  const response = await api.get<StudentDocument[]>('/documents', { params: documentFilterParams(filters) })
  return response.data
}

export async function getStudentDocuments(studentId: string, filters: DocumentFilters = {}) {
  const response = await api.get<StudentDocument[]>(`/students/${studentId}/documents`, {
    params: documentFilterParams(filters),
  })
  return response.data
}

export async function getMyDocuments(filters: DocumentFilters = {}) {
  const response = await api.get<StudentDocument[]>('/me/documents', { params: documentFilterParams(filters) })
  return response.data
}

export async function getDocumentSummary() {
  const response = await api.get<DocumentSummary>('/documents/summary')
  return response.data
}

export async function getDocumentReport() {
  const response = await api.get<DocumentReport>('/admin/reports/documents/')
  return response.data
}

export async function uploadDocument(payload: UploadDocumentPayload) {
  const response = await api.post<StudentDocument>('/documents', uploadFormData(payload), {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function uploadMyDocument(payload: UploadDocumentPayload) {
  const response = await api.post<StudentDocument>('/me/documents', uploadFormData(payload), {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function approveDocument(payload: ReviewDocumentPayload) {
  const response = await api.post<StudentDocument>(`/documents/${payload.documentId}/approve`, {
    reviewNote: payload.reviewNote,
  })
  return response.data
}

export async function rejectDocument(payload: ReviewDocumentPayload) {
  const response = await api.post<StudentDocument>(`/documents/${payload.documentId}/reject`, {
    reviewNote: payload.reviewNote,
  })
  return response.data
}

export async function archiveDocument(documentId: string) {
  const response = await api.post<StudentDocument>(`/documents/${documentId}/archive`)
  return response.data
}

export async function downloadDocument(documentId: string) {
  const response = await api.get<Blob>(`/documents/${documentId}/download`, {
    responseType: 'blob',
  })
  return {
    blob: response.data,
    contentDisposition: response.headers['content-disposition'] as string | undefined,
  }
}
