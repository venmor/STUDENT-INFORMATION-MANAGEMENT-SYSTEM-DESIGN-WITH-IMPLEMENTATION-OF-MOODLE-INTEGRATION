import { fireEvent, render, screen } from '@testing-library/react'

import { AdminMoodleSyncPage } from '@/pages/admin/MoodleSync'

const mocks = vi.hoisted(() => ({
  refetch: vi.fn(),
  retryMutate: vi.fn(),
  state: {} as Record<string, unknown>,
}))

vi.mock('@/hooks/useMoodleSync', () => ({
  useMoodleSyncSummary: () => mocks.state.summary,
  useMoodleOutboxEvents: () => mocks.state.outboxEvents,
  useMoodleUserMaps: () => mocks.state.userMaps,
  useMoodleCourseMaps: () => mocks.state.courseMaps,
  useMoodleEngagementRuns: () => mocks.state.engagementRuns,
  useMoodleEngagementSnapshots: () => mocks.state.engagementSnapshots,
  useRetryMoodleOutboxEvent: () => mocks.state.retryMutation,
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
  outbox: { pending: 2, processed: 9, failed: 1, retryable: 3 },
  mappings: { users: 7, courses: 4 },
  engagement: {
    latestRunStatus: 'SUCCEEDED',
    latestRunStartedAt: '2026-04-30T10:00:00Z',
    latestRunCompletedAt: '2026-04-30T10:01:00Z',
    latestRunSnapshots: 12,
    latestRunFailures: 0,
  },
  readiness: { moodleRestConfig: 'present', ltiConfig: 'present' },
}

const failedEvent = {
  id: 'event-1',
  eventType: 'USER_SYNC_REQUESTED',
  status: 'FAILED',
  payloadSummary: {
    userId: 42,
    sectionId: null,
    enrollmentId: null,
    studentId: null,
    gradeId: null,
    action: 'UPSERT',
  },
  attempts: 2,
  lastError: 'safe failure',
  lastAttemptAt: '2026-04-30T10:00:00Z',
  processedAt: null,
  createdAt: '2026-04-30T09:55:00Z',
  canRetry: true,
}

const userMap = {
  id: 'map-user-1',
  sisUser: { id: 42, username: 'student.one', fullName: 'Student One', email: 'student.one@example.com' },
  sisUserId: 42,
  moodleUserId: 5501,
  moodleUsername: 'student.one',
  lastSyncedAt: '2026-04-30T10:00:00Z',
  createdAt: '2026-04-30T09:00:00Z',
}

const courseMap = {
  id: 'map-course-1',
  sisSection: { id: 'section-1', courseCode: 'CSC350', courseTitle: 'Systems', sectionCode: 'A1' },
  sectionId: 'section-1',
  moodleCourseId: 8801,
  moodleShortname: 'CSC350-A1',
  moodleCategoryId: 7,
  gradeTargetConfigured: true,
  gradeComponent: 'FINAL',
  gradeActivityId: 901,
  gradeItemNumber: 0,
  gradeItemLabel: 'Final grade',
  lastSyncedAt: '2026-04-30T10:00:00Z',
  createdAt: '2026-04-30T09:00:00Z',
}

const engagementRun = {
  id: 'run-1',
  status: 'SUCCEEDED',
  dryRun: false,
  startedAt: '2026-04-30T10:00:00Z',
  completedAt: '2026-04-30T10:01:00Z',
  coursesInspected: 4,
  usersInspected: 7,
  snapshotsCreated: 10,
  snapshotsUpdated: 2,
  snapshotsTotal: 12,
  skippedUnmappedUsers: 1,
  failureCount: 0,
  lastError: '',
}

const engagementSnapshot = {
  id: 'snapshot-1',
  studentUser: { id: 42, username: 'student.one', fullName: 'Student One', email: 'student.one@example.com' },
  student: { id: 'student-1', studentNumber: '2026-CS-001' },
  section: { id: 'section-1', courseCode: 'CSC350', courseTitle: 'Systems', sectionCode: 'A1' },
  moodleUserId: 5501,
  moodleCourseId: 8801,
  moodleLastAccessAt: '2026-04-30T08:00:00Z',
  moodleCourseLastAccessAt: '2026-04-30T09:00:00Z',
  assignmentSubmissionCount: null,
  assignmentSubmissionRate: null,
  quizAttemptCount: null,
  quizAverage: null,
  forumPostCount: null,
  collectedAt: '2026-04-30T10:01:00Z',
  createdAt: '2026-04-30T10:01:00Z',
}

function setDefaultHookState(overrides: Record<string, unknown> = {}) {
  mocks.state = {
    summary: queryResult(summary),
    outboxEvents: queryResult([failedEvent]),
    userMaps: queryResult([userMap]),
    courseMaps: queryResult([courseMap]),
    engagementRuns: queryResult([engagementRun]),
    engagementSnapshots: queryResult([engagementSnapshot]),
    retryMutation: {
      mutate: mocks.retryMutate,
      isPending: false,
      variables: undefined,
    },
    ...overrides,
  }
}

describe('AdminMoodleSyncPage', () => {
  beforeEach(() => {
    mocks.refetch.mockClear()
    mocks.retryMutate.mockClear()
    setDefaultHookState()
  })

  it('renders summary cards and required dashboard sections', () => {
    const { container } = render(<AdminMoodleSyncPage />)

    expect(screen.getByText('Pending Events')).toBeInTheDocument()
    expect(screen.getByText('Processed Events')).toBeInTheDocument()
    expect(screen.getByText('Failed Events')).toBeInTheDocument()
    expect(screen.getByText('Retry Queue')).toBeInTheDocument()
    expect(screen.getByText('User Maps')).toBeInTheDocument()
    expect(screen.getByText('Course Maps')).toBeInTheDocument()
    expect(screen.getByText('Latest Ingestion')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Integration Readiness' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Operational Notes' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Integration Outbox Events' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Moodle Mappings' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Moodle Engagement Ingestion' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Current Scope' })).toBeInTheDocument()
    expect(container.textContent).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u)
  })

  it('renders outbox rows and retries failed events', () => {
    render(<AdminMoodleSyncPage />)

    expect(screen.getByText('User Sync Requested')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }))

    expect(mocks.retryMutate).toHaveBeenCalledWith('event-1', expect.any(Object))
  })

  it('renders mappings and engagement ingestion content', () => {
    render(<AdminMoodleSyncPage />)

    expect(screen.getAllByText('Student One').length).toBeGreaterThan(0)
    expect(screen.getByText('student.one@example.com')).toBeInTheDocument()
    expect(screen.getAllByText('CSC350').length).toBeGreaterThan(0)
    expect(screen.getByText('Configured')).toBeInTheDocument()
    expect(screen.getByText('Not collected in Step 3.4')).toBeInTheDocument()
  })

  it('renders empty states safely', () => {
    setDefaultHookState({
      outboxEvents: queryResult([]),
      userMaps: queryResult([]),
      courseMaps: queryResult([]),
      engagementSnapshots: queryResult([]),
    })

    render(<AdminMoodleSyncPage />)

    expect(screen.getByText('No Moodle sync events found')).toBeInTheDocument()
    expect(screen.getByText('No Moodle user mappings yet. Run Lane A user sync first.')).toBeInTheDocument()
    expect(screen.getByText('No Moodle course mappings yet. Run Lane A course sync first.')).toBeInTheDocument()
    expect(
      screen.getByText('No engagement snapshots yet. Run python manage.py ingest_moodle_engagement after Moodle mappings exist.'),
    ).toBeInTheDocument()
  })

  it('renders loading and error states safely', () => {
    setDefaultHookState({
      summary: queryResult(undefined, { isLoading: true }),
      outboxEvents: queryResult(undefined, { isError: true }),
    })

    render(<AdminMoodleSyncPage />)

    expect(screen.getByText('Loading Moodle sync dashboard')).toBeInTheDocument()
    expect(screen.getByText('Could not load Moodle sync events')).toBeInTheDocument()
    expect(screen.getByText('Check the backend API and your session permissions.')).toBeInTheDocument()
  })
})
