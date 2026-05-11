import { api } from '@/api/axios'
import type {
  ActivityReport,
  AdminReportSummary,
  CalendarDeadlineReport,
  CapacityReport,
  EnrollmentReport,
  GradeReport,
  MoodleSyncReport,
  ReportFilters,
} from '@/types/reports'

function filterParams(filters: ReportFilters = {}) {
  return {
    academic_year: filters.academicYear || undefined,
    semester: filters.semester || undefined,
    programme: filters.programme || undefined,
    course: filters.course || undefined,
    status: filters.status && filters.status !== 'ALL' ? filters.status : undefined,
  }
}

export async function getAdminReportSummary(filters: ReportFilters = {}) {
  const response = await api.get<AdminReportSummary>('/admin/reports/summary/', { params: filterParams(filters) })
  return response.data
}

export async function getEnrollmentReport(filters: ReportFilters = {}) {
  const response = await api.get<EnrollmentReport>('/admin/reports/enrollment/', { params: filterParams(filters) })
  return response.data
}

export async function getCapacityReport(filters: ReportFilters = {}) {
  const response = await api.get<CapacityReport>('/admin/reports/capacity/', { params: filterParams(filters) })
  return response.data
}

export async function getGradeReport(filters: ReportFilters = {}) {
  const response = await api.get<GradeReport>('/admin/reports/grades/', { params: filterParams(filters) })
  return response.data
}

export async function getMoodleSyncReport(filters: ReportFilters = {}) {
  const response = await api.get<MoodleSyncReport>('/admin/reports/moodle-sync/', { params: filterParams(filters) })
  return response.data
}

export async function getCalendarDeadlineReport(filters: ReportFilters = {}) {
  const response = await api.get<CalendarDeadlineReport>('/admin/reports/calendar/', { params: filterParams(filters) })
  return response.data
}

export async function getActivityReport(filters: ReportFilters = {}) {
  const response = await api.get<ActivityReport>('/admin/reports/activity/', { params: filterParams(filters) })
  return response.data
}

export async function exportCapacityReportCsv(filters: ReportFilters = {}) {
  const response = await api.get<Blob>('/admin/reports/capacity/export.csv', {
    params: filterParams(filters),
    responseType: 'blob',
  })
  return response.data
}
