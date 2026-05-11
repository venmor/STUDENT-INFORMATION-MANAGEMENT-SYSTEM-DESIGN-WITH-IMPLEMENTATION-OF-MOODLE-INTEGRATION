import { useQuery } from '@tanstack/react-query'

import {
  getActivityReport,
  getAdminReportSummary,
  getCalendarDeadlineReport,
  getCapacityReport,
  getEnrollmentReport,
  getGradeReport,
  getMoodleSyncReport,
} from '@/api/reports'
import type { ReportFilters } from '@/types/reports'

export function useAdminReportSummary(filters: ReportFilters = {}) {
  return useQuery({
    queryKey: ['admin-reports', 'summary', filters],
    queryFn: () => getAdminReportSummary(filters),
  })
}

export function useEnrollmentReport(filters: ReportFilters = {}) {
  return useQuery({
    queryKey: ['admin-reports', 'enrollment', filters],
    queryFn: () => getEnrollmentReport(filters),
  })
}

export function useCapacityReport(filters: ReportFilters = {}) {
  return useQuery({
    queryKey: ['admin-reports', 'capacity', filters],
    queryFn: () => getCapacityReport(filters),
  })
}

export function useGradeReport(filters: ReportFilters = {}) {
  return useQuery({
    queryKey: ['admin-reports', 'grades', filters],
    queryFn: () => getGradeReport(filters),
  })
}

export function useMoodleSyncReport(filters: ReportFilters = {}) {
  return useQuery({
    queryKey: ['admin-reports', 'moodle-sync', filters],
    queryFn: () => getMoodleSyncReport(filters),
  })
}

export function useCalendarDeadlineReport(filters: ReportFilters = {}) {
  return useQuery({
    queryKey: ['admin-reports', 'calendar', filters],
    queryFn: () => getCalendarDeadlineReport(filters),
  })
}

export function useActivityReport(filters: ReportFilters = {}) {
  return useQuery({
    queryKey: ['admin-reports', 'activity', filters],
    queryFn: () => getActivityReport(filters),
  })
}
