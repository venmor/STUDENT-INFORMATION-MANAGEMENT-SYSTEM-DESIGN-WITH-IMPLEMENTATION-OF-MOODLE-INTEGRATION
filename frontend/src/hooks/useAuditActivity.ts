import { useQuery } from '@tanstack/react-query'

import { getAuditActivity, getAuditEvent, getAuditSummary } from '@/api/audit'
import type { AuditFilters } from '@/types/audit'

export function useAuditActivity(filters: AuditFilters = {}) {
  return useQuery({
    queryKey: ['audit-activity', 'list', filters],
    queryFn: () => getAuditActivity(filters),
  })
}

export function useAuditSummary() {
  return useQuery({
    queryKey: ['audit-activity', 'summary'],
    queryFn: getAuditSummary,
  })
}

export function useAuditEvent(eventId?: string) {
  return useQuery({
    queryKey: ['audit-activity', 'detail', eventId],
    queryFn: () => getAuditEvent(eventId ?? ''),
    enabled: Boolean(eventId),
  })
}
