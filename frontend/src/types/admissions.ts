export type ApplicationStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'UNDER_REVIEW'
  | 'ACCEPTED'
  | 'REJECTED'
  | 'WAITLISTED'

export type ApplicantDocumentType =
  | 'TRANSCRIPT'
  | 'NATIONAL_ID'
  | 'BIRTH_CERTIFICATE'
  | 'PASSPORT_PHOTO'
  | 'OTHER'

export interface ApplicantDocument {
  id: string
  documentType: ApplicantDocumentType
  file: string
  originalFilename: string
  uploadedAt: string
}

export interface ApplicantProfile {
  id: string
  email: string
  fullName: string
  nationalId: string
  dateOfBirth: string
  gender: string
  phoneNumber: string
  programmeApplied: string | null
  programmeName: string | null
  applicationStatus: ApplicationStatus
  reviewNotes: string
  reviewedAt: string | null
  documents: ApplicantDocument[]
  createdAt: string
  updatedAt: string
}

export interface ApplicantCreatePayload {
  email: string
  full_name: string
  national_id: string
  date_of_birth: string
  gender: string
  phone_number: string
  programme_applied: string | null
}

export interface ApplicantDocumentUploadPayload {
  applicantId: string
  documentType: ApplicantDocumentType
  file: File
}

export interface ApplicationReviewPayload {
  applicantId: string
  reviewNotes?: string
}
