export type DocumentType =
  | 'NRC_ID'
  | 'OFFICIAL_LETTER'
  | 'TRANSCRIPT'
  | 'APPEAL_LETTER'
  | 'CLEARANCE_FORM'
  | 'MEDICAL_SUPPORT'
  | 'OTHER'

export type DocumentVisibility = 'ADMIN_ONLY' | 'ADMIN_ADVISOR' | 'STUDENT_VISIBLE'
export type DocumentStatus = 'PENDING_REVIEW' | 'APPROVED' | 'REJECTED' | 'ARCHIVED'

export interface DocumentStudentSummary {
  id: string
  studentNumber: string
  fullName: string
  programme: string
}

export interface DocumentUserSummary {
  id: number
  username: string
  fullName: string
}

export interface StudentDocument {
  id: string
  student: DocumentStudentSummary
  documentType: DocumentType
  title: string
  description: string
  originalFilename: string
  contentType: string
  fileSize: number
  visibility: DocumentVisibility
  status: DocumentStatus
  uploadedBy: DocumentUserSummary | null
  reviewedBy: DocumentUserSummary | null
  reviewedAt: string | null
  reviewNote: string
  metadata: Record<string, unknown>
  createdAt: string
  updatedAt: string
  canDownload: boolean
  canReview: boolean
  canArchive: boolean
}

export interface DocumentFilters {
  student?: string
  documentType?: string
  visibility?: string
  status?: string
  uploadedBy?: string
  search?: string
  dateFrom?: string
  dateTo?: string
}

export interface DocumentSummary {
  total: number
  pendingReview: number
  approved: number
  rejected: number
  archived: number
  studentVisible: number
  adminOnly: number
  recentUploads: number
  byType: Record<DocumentType, number>
}

export interface UploadDocumentPayload {
  studentId?: string
  documentType: DocumentType
  title: string
  description: string
  visibility: DocumentVisibility
  file: File
}

export interface ReviewDocumentPayload {
  documentId: string
  reviewNote: string
}

export interface DocumentReport {
  summary: DocumentSummary
  recentDocuments: Array<{
    id: string
    studentNumber: string
    studentName: string
    documentType: DocumentType
    title: string
    visibility: DocumentVisibility
    status: DocumentStatus
    createdAt: string
  }>
}
