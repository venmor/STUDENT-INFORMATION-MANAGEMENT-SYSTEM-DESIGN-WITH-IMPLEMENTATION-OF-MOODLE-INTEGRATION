import { type ReactNode, useMemo, useState } from 'react'
import {
  ArrowDownTrayIcon,
  ArrowPathIcon,
  BellAlertIcon,
  CalendarDaysIcon,
  ChartBarIcon,
  ClipboardDocumentCheckIcon,
  ExclamationTriangleIcon,
  RectangleStackIcon,
  ServerStackIcon,
  ShieldCheckIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

import { exportCapacityReportCsv } from '@/api/reports'
import { Alert } from '@/components/ui/Alert'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHead,
  DataTableHeader,
  DataTableRow,
  TableSkeleton,
} from '@/components/ui/Table'
import {
  useActivityReport,
  useAdminReportSummary,
  useCalendarDeadlineReport,
  useCapacityReport,
  useEnrollmentReport,
  useGradeReport,
  useMoodleSyncReport,
} from '@/hooks/useAdminReports'
import type {
  ActivityReport,
  AdminReportSummary,
  CalendarDeadline,
  CapacitySectionReport,
  EnrollmentStatusBreakdown,
  GradeSectionReport,
  ProgrammeBreakdown,
  ReportFilters,
} from '@/types/reports'

type BadgeTone = 'default' | 'success' | 'warning' | 'danger' | 'info'
type Accent = 'danger' | 'warning' | 'success' | 'info'

const statusItems = [
  { label: 'All', value: 'ALL' },
  { label: 'Enrolled', value: 'ENROLLED' },
  { label: 'Waitlisted', value: 'WAITLISTED' },
  { label: 'Dropped', value: 'DROPPED' },
  { label: 'Transferred', value: 'TRANSFERRED' },
  { label: 'Draft Grades', value: 'DRAFT' },
  { label: 'Official Grades', value: 'OFFICIAL' },
]

function formatNumber(value?: number | null) {
  return new Intl.NumberFormat().format(value ?? 0)
}

function formatPercent(value?: number | null) {
  return `${Number(value ?? 0).toFixed(Number(value ?? 0) % 1 === 0 ? 0 : 2)}%`
}

function formatDateTime(value?: string | null) {
  if (!value) {
    return 'Not scheduled'
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function badgeToneForStatus(status: string): BadgeTone {
  if (status === 'Complete' || status === 'Open' || status === 'OFFICIAL' || status === 'ENROLLED') {
    return 'success'
  }
  if (status === 'Full' || status === 'Over Capacity' || status === 'ERROR' || status === 'FAILED' || status === 'CRITICAL') {
    return 'danger'
  }
  if (status === 'Near Capacity' || status === 'Needs Review' || status === 'WARNING' || status === 'PARTIAL') {
    return 'warning'
  }
  return 'info'
}

function SummaryCard({
  accent,
  helper,
  icon,
  title,
  value,
}: {
  accent: Accent
  helper: string
  icon: ReactNode
  title: string
  value: string | number
}) {
  return (
    <Card accent={accent} className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-medium text-neutral-500">{title}</p>
          <p className="mt-2 truncate font-display text-2xl font-semibold text-neutral-900">{value}</p>
          <p className="mt-1 text-xs text-neutral-500">{helper}</p>
        </div>
        <div className="rounded-lg bg-white p-2 text-primary shadow-sm">{icon}</div>
      </div>
    </Card>
  )
}

function HealthBadge({ label, tone }: { label: string; tone: BadgeTone }) {
  return (
    <div className="flex min-h-11 items-center justify-between gap-3 rounded-lg border border-neutral-200 bg-white px-3 py-2">
      <span className="text-sm font-medium text-neutral-700">{label}</span>
      <Badge tone={tone}>{label.split(': ')[1]}</Badge>
    </div>
  )
}

function ProgressBar({
  label,
  value,
  width,
}: {
  label: string
  value: string
  width: number
}) {
  const safeWidth = Math.max(0, Math.min(width, 100))
  return (
    <div>
      <div className="flex items-center justify-between gap-3 text-sm">
        <span className="font-medium text-neutral-900">{label}</span>
        <span className="text-neutral-500">{value}</span>
      </div>
      <div
        className="mt-2 h-2 rounded-full bg-neutral-100"
        role="progressbar"
        aria-label={`${label}: ${value}`}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={safeWidth}
      >
        <div className="h-2 rounded-full bg-primary" style={{ width: `${safeWidth}%` }} />
      </div>
    </div>
  )
}

function StudentsByProgramme({ rows }: { rows: ProgrammeBreakdown[] }) {
  if (rows.length === 0) {
    return <EmptyState title="No student programme data" description="Create student profiles to populate programme reporting." />
  }

  return (
    <div className="space-y-4">
      {rows.map((row) => (
        <ProgressBar
          key={row.programme}
          label={row.programme}
          value={`${formatNumber(row.total)} students, ${formatPercent(row.percentage)}`}
          width={row.percentage}
        />
      ))}
    </div>
  )
}

function EnrollmentStatusChart({ rows, total }: { rows: EnrollmentStatusBreakdown[]; total: number }) {
  if (rows.length === 0) {
    return <EmptyState title="No enrollment data" description="Enrollments will appear here once students register for sections." />
  }

  return (
    <div className="space-y-4">
      {rows.map((row) => (
        <ProgressBar key={row.status} label={row.label} value={formatNumber(row.count)} width={total ? (row.count / total) * 100 : 0} />
      ))}
    </div>
  )
}

function CapacityTable({ rows, isLoading }: { rows: CapacitySectionReport[]; isLoading: boolean }) {
  if (isLoading) {
    return <TableSkeleton columns={7} />
  }
  if (rows.length === 0) {
    return <EmptyState title="No section capacity data" description="Create active sections and enrollments to populate capacity reporting." />
  }

  return (
    <DataTable ariaLabel="Section capacity report">
      <DataTableHead>
        <DataTableRow>
          <DataTableHeader>Course</DataTableHeader>
          <DataTableHeader>Section</DataTableHeader>
          <DataTableHeader>Capacity</DataTableHeader>
          <DataTableHeader>Enrolled</DataTableHeader>
          <DataTableHeader>Remaining</DataTableHeader>
          <DataTableHeader>Fill %</DataTableHeader>
          <DataTableHeader>Status</DataTableHeader>
        </DataTableRow>
      </DataTableHead>
      <DataTableBody>
        {rows.map((row) => (
          <DataTableRow key={row.sectionId}>
            <DataTableCell>
              <div className="font-medium">{row.courseCode}</div>
              <div className="mt-1 text-xs text-neutral-500">{row.courseTitle}</div>
            </DataTableCell>
            <DataTableCell>{row.sectionCode}</DataTableCell>
            <DataTableCell>{formatNumber(row.capacity)}</DataTableCell>
            <DataTableCell>{formatNumber(row.enrolledCount)}</DataTableCell>
            <DataTableCell>{formatNumber(row.remainingSeats)}</DataTableCell>
            <DataTableCell>{formatPercent(row.fillRate)}</DataTableCell>
            <DataTableCell>
              <Badge tone={badgeToneForStatus(row.status)}>{row.status}</Badge>
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}

function GradeTable({ rows, isLoading }: { rows: GradeSectionReport[]; isLoading: boolean }) {
  if (isLoading) {
    return <TableSkeleton columns={7} />
  }
  if (rows.length === 0) {
    return <EmptyState title="No grade submission data" description="Grade records will appear here after faculty enter grades." />
  }

  return (
    <DataTable ariaLabel="Grade submission progress report">
      <DataTableHead>
        <DataTableRow>
          <DataTableHeader>Section</DataTableHeader>
          <DataTableHeader>Draft</DataTableHeader>
          <DataTableHeader>Official</DataTableHeader>
          <DataTableHeader>Pending</DataTableHeader>
          <DataTableHeader>Completion %</DataTableHeader>
          <DataTableHeader>Status</DataTableHeader>
        </DataTableRow>
      </DataTableHead>
      <DataTableBody>
        {rows.map((row) => (
          <DataTableRow key={row.sectionId}>
            <DataTableCell>
              <div className="font-medium">
                {row.courseCode} {row.sectionCode}
              </div>
              <div className="mt-1 text-xs text-neutral-500">{row.facultyName}</div>
            </DataTableCell>
            <DataTableCell>{formatNumber(row.draft)}</DataTableCell>
            <DataTableCell>{formatNumber(row.official)}</DataTableCell>
            <DataTableCell>{formatNumber(row.pendingApproval)}</DataTableCell>
            <DataTableCell>{formatPercent(row.completionRate)}</DataTableCell>
            <DataTableCell>
              <Badge tone={badgeToneForStatus(row.status)}>{row.status}</Badge>
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}

function DeadlineList({ deadlines }: { deadlines: CalendarDeadline[] }) {
  if (deadlines.length === 0) {
    return <EmptyState title="No upcoming deadlines" description="Upcoming academic deadlines from the calendar will appear here." />
  }

  return (
    <div className="divide-y divide-neutral-100">
      {deadlines.map((deadline) => (
        <div key={deadline.id} className="flex items-start justify-between gap-4 py-3">
          <div>
            <p className="text-sm font-medium text-neutral-900">{deadline.title}</p>
            <p className="mt-1 text-xs text-neutral-500">
              {deadline.academicYear} {deadline.semester} - {formatDateTime(deadline.startAt)}
            </p>
          </div>
          <Badge tone={badgeToneForStatus(deadline.priority)}>{deadline.priority}</Badge>
        </div>
      ))}
    </div>
  )
}

function ActivityPanel({ activity }: { activity?: ActivityReport }) {
  const riskIndicators = activity?.riskIndicators ?? []
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg border border-neutral-200 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">Unread Notifications</p>
          <p className="mt-2 text-xl font-semibold text-neutral-900">{formatNumber(activity?.unreadAdminNotifications)}</p>
        </div>
        <div className="rounded-lg border border-neutral-200 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">Warnings</p>
          <p className="mt-2 text-xl font-semibold text-neutral-900">{formatNumber(activity?.auditWarnings)}</p>
        </div>
        <div className="rounded-lg border border-neutral-200 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">Errors</p>
          <p className="mt-2 text-xl font-semibold text-neutral-900">{formatNumber(activity?.auditErrors)}</p>
        </div>
      </div>
      {riskIndicators.length > 0 ? (
        <div className="space-y-2">
          {riskIndicators.map((indicator) => (
            <div key={indicator.label} className="flex items-center justify-between gap-3 rounded-lg bg-neutral-50 px-3 py-2">
              <span className="text-sm text-neutral-700">{indicator.label}</span>
              <Badge tone={badgeToneForStatus(indicator.severity)}>{formatNumber(indicator.count)}</Badge>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState title="No operational risk indicators" description="Operational indicators appear when existing SIS data shows issues to review." />
      )}
    </div>
  )
}

function isReportEmpty(summary?: AdminReportSummary) {
  if (!summary) {
    return false
  }
  return (
    summary.students.total === 0 &&
    summary.enrollments.total === 0 &&
    summary.capacity.sectionsTotal === 0 &&
    summary.grades.draft === 0 &&
    summary.grades.official === 0
  )
}

export function AdminReportsPage() {
  const [filters, setFilters] = useState<ReportFilters>({ status: 'ALL' })
  const [exporting, setExporting] = useState(false)
  const summaryQuery = useAdminReportSummary(filters)
  const enrollmentQuery = useEnrollmentReport(filters)
  const capacityQuery = useCapacityReport(filters)
  const gradesQuery = useGradeReport(filters)
  const moodleQuery = useMoodleSyncReport(filters)
  const calendarQuery = useCalendarDeadlineReport(filters)
  const activityQuery = useActivityReport(filters)

  const reportQueries = useMemo(
    () => [summaryQuery, enrollmentQuery, capacityQuery, gradesQuery, moodleQuery, calendarQuery, activityQuery],
    [activityQuery, calendarQuery, capacityQuery, enrollmentQuery, gradesQuery, moodleQuery, summaryQuery],
  )

  const summary = summaryQuery.data
  const hasError = reportQueries.some((query) => query.isError)
  const isLoading = summaryQuery.isLoading
  const empty = isReportEmpty(summary)
  const moodleHealth = summary && summary.moodle.failedEvents === 0 && summary.moodle.latestEngagementRunStatus !== 'FAILED' && summary.moodle.latestEngagementRunStatus !== 'PARTIAL'
  const gradeOnTrack = (summary?.grades.completionRate ?? 0) >= 80
  const capacityPressure = (summary?.capacity.sectionsNearCapacity ?? 0) > 0 || (summary?.capacity.sectionsFull ?? 0) > 0
  const deadlineTone: BadgeTone = (summary?.calendar.criticalDeadlines ?? 0) > 0 ? 'danger' : (summary?.calendar.upcomingDeadlines ?? 0) > 0 ? 'warning' : 'success'
  const auditWarnings = (activityQuery.data?.auditErrors ?? 0) > 0 || (activityQuery.data?.auditWarnings ?? 0) > 0

  function updateFilter(key: keyof ReportFilters, value: string) {
    setFilters((current) => ({ ...current, [key]: value }))
  }

  function refreshReports() {
    reportQueries.forEach((query) => query.refetch())
  }

  async function exportCapacity() {
    setExporting(true)
    try {
      const blob = await exportCapacityReportCsv(filters)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'section-capacity-report.csv'
      link.click()
      URL.revokeObjectURL(url)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 rounded-card border border-neutral-200 bg-white p-4 shadow-card lg:flex-row lg:items-end lg:justify-between">
        <div className="grid flex-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <Input
            id="report-academic-year"
            label="Academic year"
            value={filters.academicYear ?? ''}
            placeholder="2026/2027"
            onChange={(event) => updateFilter('academicYear', event.target.value)}
          />
          <Input
            id="report-semester"
            label="Semester"
            value={filters.semester ?? ''}
            placeholder="Semester 1"
            onChange={(event) => updateFilter('semester', event.target.value)}
          />
          <Input
            id="report-programme"
            label="Programme"
            value={filters.programme ?? ''}
            placeholder="BSc Computer Science"
            onChange={(event) => updateFilter('programme', event.target.value)}
          />
          <Input
            id="report-course"
            label="Course"
            value={filters.course ?? ''}
            placeholder="CSC351"
            onChange={(event) => updateFilter('course', event.target.value)}
          />
          <Select id="report-status" label="Status" items={statusItems} value={filters.status ?? 'ALL'} onValueChange={(value) => updateFilter('status', value)} />
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={refreshReports} icon={<ArrowPathIcon className="h-4 w-4" />}>
            Refresh
          </Button>
          <Button variant="secondary" onClick={exportCapacity} loading={exporting} icon={<ArrowDownTrayIcon className="h-4 w-4" />}>
            Export Capacity CSV
          </Button>
          <Link className="inline-flex min-h-11 items-center justify-center rounded-lg border border-neutral-200 px-3 text-sm font-semibold text-primary hover:bg-primary-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50" to="/admin/moodle-sync">
            Open Moodle Sync
          </Link>
          <Link className="inline-flex min-h-11 items-center justify-center rounded-lg border border-neutral-200 px-3 text-sm font-semibold text-primary hover:bg-primary-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50" to="/calendar">
            Open Calendar
          </Link>
          <Link className="inline-flex min-h-11 items-center justify-center rounded-lg border border-neutral-200 px-3 text-sm font-semibold text-primary hover:bg-primary-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50" to="/admin/audit-log">
            Open Audit Log
          </Link>
        </div>
      </div>

      {isLoading ? <Alert title="Loading institution reports">Fetching the latest reporting data.</Alert> : null}
      {hasError ? (
        <Alert tone="danger" title="Could not load institution reports" icon={<ExclamationTriangleIcon className="h-5 w-5" />}>
          Check the backend API and your admin session.
        </Alert>
      ) : null}
      {empty ? (
        <EmptyState
          title="No report data available yet"
          description="Create students, sections, enrollments, grades, Moodle sync events, or calendar deadlines to populate this report."
          icon={<ChartBarIcon className="h-10 w-10" />}
        />
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-7">
        <SummaryCard title="Active Students" value={formatNumber(summary?.students.active)} helper={`${formatNumber(summary?.students.inactive)} inactive`} accent="info" icon={<UserGroupIcon className="h-5 w-5" />} />
        <SummaryCard title="Current Enrollments" value={formatNumber(summary?.enrollments.currentTerm)} helper={`${formatNumber(summary?.enrollments.pending)} waitlisted`} accent="success" icon={<RectangleStackIcon className="h-5 w-5" />} />
        <SummaryCard title="Sections Near Capacity" value={formatNumber(summary?.capacity.sectionsNearCapacity)} helper={`${formatNumber(summary?.capacity.sectionsFull)} full or over`} accent={capacityPressure ? 'warning' : 'success'} icon={<ChartBarIcon className="h-5 w-5" />} />
        <SummaryCard title="Official Grades" value={formatNumber(summary?.grades.official)} helper={`${formatPercent(summary?.grades.completionRate)} complete`} accent={gradeOnTrack ? 'success' : 'warning'} icon={<ClipboardDocumentCheckIcon className="h-5 w-5" />} />
        <SummaryCard title="Moodle Sync" value={moodleHealth ? 'Healthy' : 'Review'} helper={`${formatNumber(summary?.moodle.failedEvents)} failed events`} accent={moodleHealth ? 'success' : 'danger'} icon={<ServerStackIcon className="h-5 w-5" />} />
        <SummaryCard title="Upcoming Deadlines" value={formatNumber(summary?.calendar.upcomingDeadlines)} helper={summary?.calendar.nextDeadlineTitle ?? 'No next deadline'} accent={deadlineTone === 'danger' ? 'danger' : 'info'} icon={<CalendarDaysIcon className="h-5 w-5" />} />
        <SummaryCard title="Audit Events Today" value={formatNumber(summary?.activity.auditEventsToday)} helper={`${formatNumber(summary?.activity.unreadAdminNotifications)} unread admin notices`} accent={auditWarnings ? 'warning' : 'info'} icon={<ShieldCheckIcon className="h-5 w-5" />} />
      </div>

      <div className="grid gap-3 md:grid-cols-5">
        <HealthBadge label={`Moodle Sync: ${moodleHealth ? 'Healthy' : 'Attention Needed'}`} tone={moodleHealth ? 'success' : 'danger'} />
        <HealthBadge label={`Grade Completion: ${gradeOnTrack ? 'On Track' : 'Needs Review'}`} tone={gradeOnTrack ? 'success' : 'warning'} />
        <HealthBadge label={`Capacity: ${capacityPressure ? 'Near Capacity' : 'Normal'}`} tone={capacityPressure ? 'warning' : 'success'} />
        <HealthBadge label={`Deadlines: ${deadlineTone === 'danger' ? 'Critical' : deadlineTone === 'warning' ? 'Upcoming' : 'Clear'}`} tone={deadlineTone} />
        <HealthBadge label={`Audit: ${auditWarnings ? 'Warnings' : 'Normal'}`} tone={auditWarnings ? 'warning' : 'success'} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardTitle>Students by Programme</CardTitle>
          <div className="mt-4">
            <StudentsByProgramme rows={summary?.students.byProgramme ?? []} />
          </div>
        </Card>
        <Card>
          <CardTitle>Enrollment Status</CardTitle>
          <div className="mt-4">
            <EnrollmentStatusChart rows={enrollmentQuery.data?.statusBreakdown ?? []} total={enrollmentQuery.data?.total ?? 0} />
          </div>
        </Card>
      </div>

      <div className="grid gap-6">
        <Card>
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle>Section Capacity</CardTitle>
            <Link className="text-sm font-semibold text-primary hover:text-primary-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50" to="/admin/courses">
              Open Courses
            </Link>
          </div>
          <CapacityTable rows={capacityQuery.data?.sections ?? []} isLoading={capacityQuery.isLoading} />
        </Card>
        <Card>
          <CardTitle>Grade Submission Progress</CardTitle>
          <div className="mt-4">
            <GradeTable rows={gradesQuery.data?.sections ?? []} isLoading={gradesQuery.isLoading} />
          </div>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <Card>
          <CardTitle>Moodle Sync Health</CardTitle>
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between gap-3"><span>Pending</span><strong>{formatNumber(moodleQuery.data?.outbox.pending)}</strong></div>
            <div className="flex justify-between gap-3"><span>Processed</span><strong>{formatNumber(moodleQuery.data?.outbox.processed)}</strong></div>
            <div className="flex justify-between gap-3"><span>Failed</span><strong>{formatNumber(moodleQuery.data?.outbox.failed)}</strong></div>
            <div className="flex justify-between gap-3"><span>Retryable</span><strong>{formatNumber(moodleQuery.data?.outbox.retryable)}</strong></div>
            <div className="rounded-lg bg-neutral-50 p-3">
              <p className="font-medium text-neutral-900">Latest ingestion run</p>
              <p className="mt-1 text-neutral-500">{moodleQuery.data?.latestEngagementRun?.status ?? 'No ingestion run yet'}</p>
            </div>
            <Link className="inline-flex min-h-11 items-center font-semibold text-primary hover:text-primary-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50" to="/admin/moodle-sync">
              Review Moodle Sync
            </Link>
          </div>
        </Card>
        <Card>
          <div className="mb-2 flex items-center justify-between gap-3">
            <CardTitle>Upcoming Academic Deadlines</CardTitle>
            <Link className="text-sm font-semibold text-primary hover:text-primary-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50" to="/calendar">
              Review Deadlines
            </Link>
          </div>
          <DeadlineList deadlines={calendarQuery.data?.deadlines ?? []} />
        </Card>
        <Card>
          <div className="mb-4 flex items-center justify-between gap-3">
            <CardTitle>Operational Activity</CardTitle>
            <Link className="text-sm font-semibold text-primary hover:text-primary-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50" to="/admin/audit-log">
              Review Activity
            </Link>
          </div>
          <ActivityPanel activity={activityQuery.data} />
        </Card>
      </div>

      <Card>
        <div className="flex items-start gap-3">
          <BellAlertIcon className="mt-0.5 h-5 w-5 text-primary" />
          <div>
            <CardTitle>Current Scope</CardTitle>
            <p className="mt-2 text-sm leading-6 text-neutral-600">
              This dashboard summarizes existing SIS, Moodle, calendar, notification, and audit data. It does not implement document management, admissions, AI, at-risk scoring, external BI, financial billing, or Step 3.5F Student Document Management. Step 3.5F Student Document Management remains the next planned slice.
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
