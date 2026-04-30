import { fireEvent, render, screen } from '@testing-library/react'

import { AdminAuditLogPage } from '@/pages/admin/AuditLog'

const mocks = vi.hoisted(() => ({
  refetch: vi.fn(),
  state: {} as Record<string, unknown>,
}))

vi.mock('@/hooks/useAuditActivity', () => ({
  useAuditSummary: () => mocks.state.summary,
  useAuditActivity: () => mocks.state.activity,
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
  total: 12,
  errors: 2,
  warnings: 1,
  today: 5,
  byCategory: {
    USER: 2,
    STUDENT_RECORD: 0,
    COURSE: 0,
    ENROLLMENT: 1,
    GRADE: 1,
    MOODLE: 4,
    NOTIFICATION: 3,
    LTI: 1,
    SYSTEM: 0,
    AI: 0,
  },
}

const auditEvent = {
  id: 'audit-event-1',
  actor: {
    id: 1,
    username: 'admin.one',
    fullName: 'Admin One',
    role: 'ADMIN',
  },
  category: 'MOODLE',
  action: 'MOODLE_SYNC_FAILED',
  severity: 'ERROR',
  summary: 'Moodle sync failed for GRADE_SYNC_REQUESTED.',
  targetType: 'IntegrationOutboxEvent',
  targetId: 'event-1234567890',
  metadata: {
    eventType: 'GRADE_SYNC_REQUESTED',
    safeError: 'Moodle REST returned invalid JSON.',
  },
  createdAt: '2026-04-30T12:00:00Z',
}

function setDefaultHookState(overrides: Record<string, unknown> = {}) {
  mocks.state = {
    summary: queryResult(summary),
    activity: queryResult([auditEvent]),
    ...overrides,
  }
}

describe('AdminAuditLogPage', () => {
  beforeEach(() => {
    mocks.refetch.mockClear()
    setDefaultHookState()
  })

  it('renders the real activity viewer, summary cards, filters, and table without emoji labels', () => {
    const { container } = render(<AdminAuditLogPage />)

    expect(screen.getByText('Total Events')).toBeInTheDocument()
    expect(screen.getByText('Errors')).toBeInTheDocument()
    expect(screen.getByText('Warnings')).toBeInTheDocument()
    expect(screen.getByText('Today')).toBeInTheDocument()
    expect(screen.getAllByText('Moodle').length).toBeGreaterThan(0)
    expect(screen.getByText('User Activity')).toBeInTheDocument()
    expect(screen.getByText('Notifications')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Admin Activity Viewer' })).toBeInTheDocument()
    expect(screen.getByText('Read-only timeline of important SIS, Moodle, notification, and governance activity.')).toBeInTheDocument()
    expect(screen.getByLabelText('Category')).toBeInTheDocument()
    expect(screen.getByLabelText('Severity')).toBeInTheDocument()
    expect(screen.getByLabelText('Action search')).toBeInTheDocument()
    expect(screen.getByText('MOODLE_SYNC_FAILED')).toBeInTheDocument()
    expect(screen.getByText('Moodle sync failed for GRADE_SYNC_REQUESTED.')).toBeInTheDocument()
    expect(container.textContent).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u)
  })

  it('opens the details panel with sanitized metadata', () => {
    render(<AdminAuditLogPage />)

    fireEvent.click(screen.getByRole('button', { name: 'Details' }))

    expect(screen.getByRole('heading', { name: 'Activity Details' })).toBeInTheDocument()
    expect(screen.getByText('IntegrationOutboxEvent')).toBeInTheDocument()
    expect(screen.getByText('eventType')).toBeInTheDocument()
    expect(screen.getByText('GRADE_SYNC_REQUESTED')).toBeInTheDocument()
    expect(screen.getByText('safeError')).toBeInTheDocument()
    expect(screen.getByText('Moodle REST returned invalid JSON.')).toBeInTheDocument()
  })

  it('renders empty state', () => {
    setDefaultHookState({
      activity: queryResult([]),
    })

    render(<AdminAuditLogPage />)

    expect(screen.getByText('No audit activity found')).toBeInTheDocument()
    expect(screen.getByText('Activity will appear here when users, Moodle sync, notifications, and governed actions occur.')).toBeInTheDocument()
  })

  it('renders loading and error states safely', () => {
    setDefaultHookState({
      summary: queryResult(undefined, { isLoading: true }),
      activity: queryResult(undefined, { isError: true }),
    })

    render(<AdminAuditLogPage />)

    expect(screen.getByText('Loading audit activity')).toBeInTheDocument()
    expect(screen.getByText('Could not load audit activity')).toBeInTheDocument()
    expect(screen.getByText('Check the backend API and your admin session.')).toBeInTheDocument()
  })
})
