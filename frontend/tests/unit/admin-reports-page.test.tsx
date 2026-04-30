import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { AdminReportsPage } from '@/pages/admin/Reports'

const mocks = vi.hoisted(() => ({
  refetch: vi.fn(),
  state: {} as Record<string, unknown>,
}))

vi.mock('@/hooks/useAdminReports', () => ({
  useAdminReportSummary: () => mocks.state.summary,
  useEnrollmentReport: () => mocks.state.enrollment,
  useCapacityReport: () => mocks.state.capacity,
  useGradeReport: () => mocks.state.grades,
  useMoodleSyncReport: () => mocks.state.moodle,
  useCalendarDeadlineReport: () => mocks.state.calendar,
  useActivityReport: () => mocks.state.activity,
}))

function queryResult(data: unknown, overrides: Record<string, unknown> = {}) {
  return {
    data,
    isLoading: false,
    isError: false,
    refetch: mocks.refetch,
    ...overrides,
  }
}

const summary = {
  students: {
    total: 5,
    active: 4,
    inactive: 1,
    byProgramme: [
      { programme: 'BSc Computer Science', total: 4, active: 4, inactive: 0, percentage: 80 },
      { programme: 'BSc Information Systems', total: 1, active: 0, inactive: 1, percentage: 20 },
    ],
  },
  enrollments: { total: 11, currentTerm: 11, pending: 1, confirmed: 9, dropped: 1 },
  capacity: { sectionsTotal: 4, sectionsNearCapacity: 1, sectionsFull: 2, averageFillRate: 97.5 },
  grades: { draft: 1, official: 4, pendingApproval: 0, completionRate: 44.44 },
  moodle: {
    pendingEvents: 1,
    failedEvents: 1,
    processedEvents: 1,
    userMappings: 1,
    courseMappings: 1,
    latestEngagementRunStatus: 'PARTIAL',
  },
  calendar: {
    upcomingDeadlines: 3,
    criticalDeadlines: 1,
    nextDeadlineTitle: 'Registration deadline',
    nextDeadlineAt: '2026-05-02T08:00:00Z',
  },
  activity: { auditEventsToday: 2, unreadAdminNotifications: 1 },
}

const enrollment = {
  total: 11,
  statusBreakdown: [
    { status: 'ENROLLED', label: 'Enrolled', count: 9 },
    { status: 'WAITLISTED', label: 'Waitlisted', count: 1 },
    { status: 'DROPPED', label: 'Dropped', count: 1 },
    { status: 'TRANSFERRED', label: 'Transferred', count: 0 },
  ],
  byProgramme: [{ programme: 'BSc Computer Science', count: 10 }],
  byCourseSection: [],
  topSections: [],
  recentActivity: [],
}

const capacity = {
  sections: [
    {
      sectionId: 'section-1',
      courseCode: 'CSC351',
      courseTitle: 'Distributed Systems',
      sectionCode: 'A1',
      academicYear: '2026/2027',
      semester: 'Semester 1',
      facultyName: 'Faculty Demo',
      capacity: 2,
      enrolledCount: 2,
      remainingSeats: 0,
      fillRate: 100,
      status: 'Full',
    },
  ],
  nearOrFullSections: [],
  summary: { sectionsTotal: 1, sectionsNearCapacity: 0, sectionsFull: 1, averageFillRate: 100 },
}

const grades = {
  totals: { draft: 1, official: 4, pendingApproval: 0, completionRate: 44.44, sectionsWithMissingSubmissions: 1 },
  statusBreakdown: [
    { status: 'DRAFT', label: 'Draft', count: 1 },
    { status: 'OFFICIAL', label: 'Official', count: 4 },
  ],
  sections: [
    {
      sectionId: 'section-1',
      courseCode: 'CSC351',
      courseTitle: 'Distributed Systems',
      sectionCode: 'A1',
      facultyName: 'Faculty Demo',
      academicYear: '2026/2027',
      semester: 'Semester 1',
      enrolledCount: 2,
      draft: 1,
      official: 1,
      pendingApproval: 0,
      missingSubmissions: 0,
      completionRate: 50,
      status: 'Needs Review',
    },
  ],
  sectionsWithMissingSubmissions: [],
}

const moodle = {
  outbox: { pending: 1, processed: 1, failed: 1, retryable: 2 },
  mappings: { users: 1, courses: 1 },
  latestFailedEvent: {
    id: 'event-1',
    eventType: 'GRADE_SYNC_REQUESTED',
    attempts: 2,
    lastError: 'Safe failure',
    lastAttemptAt: '2026-05-01T10:00:00Z',
    createdAt: '2026-05-01T09:00:00Z',
  },
  latestEngagementRun: {
    id: 'run-1',
    status: 'PARTIAL',
    dryRun: false,
    startedAt: '2026-05-01T10:00:00Z',
    completedAt: '2026-05-01T10:01:00Z',
    coursesInspected: 1,
    usersInspected: 2,
    snapshotsTotal: 1,
    failureCount: 1,
    lastError: 'safe partial failure',
  },
  recentIngestionFailures: [],
}

const calendar = {
  upcomingNext7Days: 2,
  upcomingNext30Days: 3,
  criticalDeadlines: 1,
  highPriorityEvents: 2,
  registrationDeadlines: 1,
  examPeriods: 1,
  gradeSubmissionDeadlines: 1,
  nextDeadline: {
    id: 'deadline-1',
    title: 'Registration deadline',
    eventType: 'REGISTRATION_DEADLINE',
    priority: 'CRITICAL',
    academicYear: '2026/2027',
    semester: 'Semester 1',
    startAt: '2026-05-02T08:00:00Z',
  },
  deadlines: [
    {
      id: 'deadline-1',
      title: 'Registration deadline',
      eventType: 'REGISTRATION_DEADLINE',
      priority: 'CRITICAL',
      academicYear: '2026/2027',
      semester: 'Semester 1',
      startAt: '2026-05-02T08:00:00Z',
    },
  ],
}

const activity = {
  unreadAdminNotifications: 1,
  auditEventsToday: 2,
  auditWarnings: 1,
  auditErrors: 1,
  byCategory: { SYSTEM: 1, MOODLE: 1 },
  commonCategories: [{ category: 'MOODLE', count: 1 }],
  recentHighSeverityAuditEvents: [
    {
      id: 'audit-1',
      category: 'MOODLE',
      action: 'MOODLE_SYNC_FAILED',
      severity: 'ERROR',
      summary: 'Moodle failure.',
      createdAt: '2026-05-01T09:00:00Z',
    },
  ],
  riskIndicators: [
    { label: 'Failed Moodle sync events', count: 1, severity: 'ERROR', actionUrl: '/admin/moodle-sync' },
    { label: 'Active financial flags', count: 1, severity: 'WARNING', actionUrl: '/admin/reports' },
  ],
}

function setDefaultHookState(overrides: Record<string, unknown> = {}) {
  mocks.state = {
    summary: queryResult(summary),
    enrollment: queryResult(enrollment),
    capacity: queryResult(capacity),
    grades: queryResult(grades),
    moodle: queryResult(moodle),
    calendar: queryResult(calendar),
    activity: queryResult(activity),
    ...overrides,
  }
}

describe('AdminReportsPage', () => {
  beforeEach(() => {
    mocks.refetch.mockClear()
    setDefaultHookState()
  })

  it('renders summary cards, health strip, filters, report tables, links, and no emoji text', () => {
    const { container } = render(
      <MemoryRouter>
        <AdminReportsPage />
      </MemoryRouter>,
    )

    expect(screen.getByText('Active Students')).toBeInTheDocument()
    expect(screen.getByText('Current Enrollments')).toBeInTheDocument()
    expect(screen.getByText('Sections Near Capacity')).toBeInTheDocument()
    expect(screen.getByText('Official Grades')).toBeInTheDocument()
    expect(screen.getByText('Moodle Sync Health')).toBeInTheDocument()
    expect(screen.getByText('Upcoming Deadlines')).toBeInTheDocument()
    expect(screen.getByText('Audit Events Today')).toBeInTheDocument()
    expect(screen.getByText('Moodle Sync: Attention Needed')).toBeInTheDocument()
    expect(screen.getByText('Grade Completion: Needs Review')).toBeInTheDocument()
    expect(screen.getByText('Capacity: Near Capacity')).toBeInTheDocument()
    expect(screen.getByText('Deadlines: Critical')).toBeInTheDocument()
    expect(screen.getByText('Audit: Warnings')).toBeInTheDocument()
    expect(screen.getByLabelText('Academic year')).toBeInTheDocument()
    expect(screen.getByLabelText('Semester')).toBeInTheDocument()
    expect(screen.getByLabelText('Programme')).toBeInTheDocument()
    expect(screen.getByLabelText('Course')).toBeInTheDocument()
    expect(screen.getByLabelText('Status')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Students by Programme' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Enrollment Status' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Section Capacity' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Grade Submission Progress' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Upcoming Academic Deadlines' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Operational Activity' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Current Scope' })).toBeInTheDocument()
    expect(screen.getByText('CSC351')).toBeInTheDocument()
    expect(screen.getAllByText('Needs Review').length).toBeGreaterThan(0)
    expect(screen.getByRole('link', { name: 'Open Moodle Sync' })).toHaveAttribute('href', '/admin/moodle-sync')
    expect(screen.getByRole('link', { name: 'Open Calendar' })).toHaveAttribute('href', '/calendar')
    expect(screen.getByRole('link', { name: 'Open Audit Log' })).toHaveAttribute('href', '/admin/audit-log')
    expect(container.textContent).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u)
  })

  it('refreshes all reports from the action row', () => {
    render(
      <MemoryRouter>
        <AdminReportsPage />
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Refresh' }))

    expect(mocks.refetch).toHaveBeenCalledTimes(7)
  })

  it('renders empty state when no report data exists', () => {
    setDefaultHookState({
      summary: queryResult({
        ...summary,
        students: { total: 0, active: 0, inactive: 0, byProgramme: [] },
        enrollments: { total: 0, currentTerm: 0, pending: 0, confirmed: 0, dropped: 0 },
        capacity: { sectionsTotal: 0, sectionsNearCapacity: 0, sectionsFull: 0, averageFillRate: 0 },
        grades: { draft: 0, official: 0, pendingApproval: 0, completionRate: 0 },
      }),
      enrollment: queryResult({ ...enrollment, statusBreakdown: [], byProgramme: [] }),
      capacity: queryResult({ ...capacity, sections: [] }),
      grades: queryResult({ ...grades, sections: [] }),
      calendar: queryResult({ ...calendar, deadlines: [], nextDeadline: null }),
      activity: queryResult({ ...activity, riskIndicators: [] }),
    })

    render(
      <MemoryRouter>
        <AdminReportsPage />
      </MemoryRouter>,
    )

    expect(screen.getByText('No report data available yet')).toBeInTheDocument()
    expect(
      screen.getByText('Create students, sections, enrollments, grades, Moodle sync events, or calendar deadlines to populate this report.'),
    ).toBeInTheDocument()
  })

  it('renders loading and error states safely', () => {
    setDefaultHookState({
      summary: queryResult(undefined, { isLoading: true }),
      capacity: queryResult(undefined, { isError: true }),
    })

    render(
      <MemoryRouter>
        <AdminReportsPage />
      </MemoryRouter>,
    )

    expect(screen.getByText('Loading institution reports')).toBeInTheDocument()
    expect(screen.getByText('Could not load institution reports')).toBeInTheDocument()
    expect(screen.getByText('Check the backend API and your admin session.')).toBeInTheDocument()
  })
})
