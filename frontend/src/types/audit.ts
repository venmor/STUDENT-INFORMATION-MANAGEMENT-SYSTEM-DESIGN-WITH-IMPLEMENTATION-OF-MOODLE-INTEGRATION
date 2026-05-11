export type AuditCategory =
  | 'USER'
  | 'STUDENT_RECORD'
  | 'COURSE'
  | 'ENROLLMENT'
  | 'GRADE'
  | 'MOODLE'
  | 'NOTIFICATION'
  | 'LTI'
  | 'SYSTEM'
  | 'AI'

export type AuditSeverity = 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR'

export interface AuditActor {
  id: number | null
  username: string
  fullName: string
  role: string
}

export interface AuditEvent {
  id: string
  actor: AuditActor | null
  category: AuditCategory
  action: string
  severity: AuditSeverity
  summary: string
  targetType: string
  targetId: string
  metadata: Record<string, unknown>
  ipAddress?: string | null
  userAgent?: string
  createdAt: string
}

export interface AuditSummary {
  total: number
  errors: number
  warnings: number
  today: number
  byCategory: Record<AuditCategory, number>
}

export interface AuditFilters {
  category?: AuditCategory | 'ALL'
  severity?: AuditSeverity | 'ALL'
  action?: string
  actor?: string
  search?: string
  dateFrom?: string
  dateTo?: string
  limit?: number
}
