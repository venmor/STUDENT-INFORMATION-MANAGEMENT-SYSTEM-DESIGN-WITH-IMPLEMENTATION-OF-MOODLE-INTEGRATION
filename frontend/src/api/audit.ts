import { api } from '@/api/axios'
import type { AuditEvent, AuditFilters, AuditSummary } from '@/types/audit'

function filterParam(value?: string) {
  return value && value !== 'ALL' ? value : undefined
}

export async function getAuditActivity(filters: AuditFilters = {}) {
  const response = await api.get<AuditEvent[]>('/admin/activity', {
    params: {
      category: filterParam(filters.category),
      severity: filterParam(filters.severity),
      action: filters.action || undefined,
      actor: filters.actor || undefined,
      search: filters.search || undefined,
      date_from: filters.dateFrom || undefined,
      date_to: filters.dateTo || undefined,
      limit: filters.limit,
    },
  })
  return response.data
}

export async function getAuditSummary() {
  const response = await api.get<AuditSummary>('/admin/activity/summary')
  return response.data
}

export async function getAuditEvent(eventId: string) {
  const response = await api.get<AuditEvent>(`/admin/activity/${eventId}`)
  return response.data
}
