import type { DocumentStatus, DocumentType, DocumentVisibility } from '@/types/documents'

export type BadgeTone = 'default' | 'success' | 'warning' | 'danger' | 'info'

export const documentTypeOptions: Array<{ label: string; value: DocumentType }> = [
  { value: 'NRC_ID', label: 'NRC/ID' },
  { value: 'OFFICIAL_LETTER', label: 'Official Letter' },
  { value: 'TRANSCRIPT', label: 'Transcript' },
  { value: 'APPEAL_LETTER', label: 'Appeal Letter' },
  { value: 'CLEARANCE_FORM', label: 'Clearance Form' },
  { value: 'MEDICAL_SUPPORT', label: 'Medical Supporting Document' },
  { value: 'OTHER', label: 'Other Supporting Document' },
]

export const documentStatusOptions: Array<{ label: string; value: DocumentStatus }> = [
  { value: 'PENDING_REVIEW', label: 'Pending Review' },
  { value: 'APPROVED', label: 'Approved' },
  { value: 'REJECTED', label: 'Rejected' },
  { value: 'ARCHIVED', label: 'Archived' },
]

export const documentVisibilityOptions: Array<{ label: string; value: DocumentVisibility }> = [
  { value: 'ADMIN_ONLY', label: 'Admin Only' },
  { value: 'ADMIN_ADVISOR', label: 'Admin and Advisor' },
  { value: 'STUDENT_VISIBLE', label: 'Student Visible' },
]

export function documentTypeLabel(value: string) {
  return documentTypeOptions.find((item) => item.value === value)?.label ?? value
}

export function documentStatusLabel(value: string) {
  return documentStatusOptions.find((item) => item.value === value)?.label ?? value
}

export function documentVisibilityLabel(value: string) {
  return documentVisibilityOptions.find((item) => item.value === value)?.label ?? value
}

export function documentStatusTone(value: string): BadgeTone {
  if (value === 'APPROVED') {
    return 'success'
  }
  if (value === 'REJECTED') {
    return 'danger'
  }
  if (value === 'ARCHIVED') {
    return 'default'
  }
  return 'warning'
}

export function documentVisibilityTone(value: string): BadgeTone {
  if (value === 'STUDENT_VISIBLE') {
    return 'success'
  }
  if (value === 'ADMIN_ADVISOR') {
    return 'info'
  }
  return 'warning'
}
