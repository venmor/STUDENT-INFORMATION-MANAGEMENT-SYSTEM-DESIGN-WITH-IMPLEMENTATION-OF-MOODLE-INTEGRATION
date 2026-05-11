import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { NotificationsPage } from '@/pages/Notifications'

const mocks = vi.hoisted(() => ({
  markAllMutate: vi.fn(),
  markReadMutate: vi.fn(),
  state: {} as Record<string, unknown>,
}))

vi.mock('@/hooks/useNotifications', () => ({
  useNotificationSummary: () => mocks.state.summary,
  useNotifications: () => mocks.state.notifications,
  useMarkNotificationRead: () => mocks.state.markRead,
  useMarkAllNotificationsRead: () => mocks.state.markAll,
}))

function queryResult(data: unknown, overrides: Record<string, unknown> = {}) {
  return {
    data,
    isLoading: false,
    isError: false,
    ...overrides,
  }
}

const summary = {
  unreadCount: 2,
  byCategory: {
    ACADEMIC: 0,
    MOODLE: 1,
    GRADES: 1,
    ENROLLMENT: 0,
    ADVISING: 0,
    SYSTEM: 0,
  },
  latest: [],
}

const moodleNotification = {
  id: 'notification-1',
  category: 'MOODLE',
  severity: 'ERROR',
  title: 'Moodle sync failed',
  message: 'GRADE_SYNC_REQUESTED failed safely.',
  actionLabel: 'Open Moodle Sync',
  actionUrl: '/admin/moodle-sync',
  isRead: false,
  readAt: null,
  createdAt: '2026-04-30T12:00:00Z',
  sourceType: 'IntegrationOutboxEvent',
  sourceId: 'event-1',
}

const gradeNotification = {
  id: 'notification-2',
  category: 'GRADES',
  severity: 'SUCCESS',
  title: 'Grade released',
  message: 'Your official grade is available.',
  actionLabel: 'View grades',
  actionUrl: '/student/grades',
  isRead: true,
  readAt: '2026-04-30T12:05:00Z',
  createdAt: '2026-04-30T12:01:00Z',
  sourceType: 'GradeRecord',
  sourceId: 'grade-1',
}

function setDefaultHookState(overrides: Record<string, unknown> = {}) {
  mocks.state = {
    summary: queryResult(summary),
    notifications: queryResult([moodleNotification, gradeNotification]),
    markRead: {
      mutate: mocks.markReadMutate,
      isPending: false,
      variables: undefined,
    },
    markAll: {
      mutate: mocks.markAllMutate,
      isPending: false,
    },
    ...overrides,
  }
}

function renderPage() {
  return render(
    <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
      <NotificationsPage />
    </MemoryRouter>,
  )
}

describe('NotificationsPage', () => {
  beforeEach(() => {
    mocks.markAllMutate.mockClear()
    mocks.markReadMutate.mockClear()
    setDefaultHookState()
  })

  it('renders summary cards, filters, and notification list without emoji labels', () => {
    const { container } = renderPage()

    expect(screen.getByText('Unread')).toBeInTheDocument()
    expect(screen.getAllByText('Moodle').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Grades').length).toBeGreaterThan(0)
    expect(screen.getByText('Enrollment')).toBeInTheDocument()
    expect(screen.getByText('Advising')).toBeInTheDocument()
    expect(screen.getByText('System')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Notification Center' })).toBeInTheDocument()
    expect(screen.getByLabelText('Status')).toBeInTheDocument()
    expect(screen.getByLabelText('Category')).toBeInTheDocument()
    expect(screen.getByLabelText('Severity')).toBeInTheDocument()
    expect(screen.getByText('Moodle sync failed')).toBeInTheDocument()
    expect(screen.getByText('Grade released')).toBeInTheDocument()
    expect(container.textContent).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u)
  })

  it('marks one notification and all notifications as read', () => {
    renderPage()

    fireEvent.click(screen.getByRole('button', { name: 'Mark as read' }))
    fireEvent.click(screen.getByRole('button', { name: 'Mark all as read' }))

    expect(mocks.markReadMutate).toHaveBeenCalledWith('notification-1')
    expect(mocks.markAllMutate).toHaveBeenCalled()
  })

  it('disables mark all as read when there are no unread notifications', () => {
    setDefaultHookState({
      summary: queryResult({
        ...summary,
        unreadCount: 0,
      }),
    })

    renderPage()

    expect(screen.getByRole('button', { name: 'Mark all as read' })).toBeDisabled()
  })

  it('renders empty state', () => {
    setDefaultHookState({
      summary: queryResult({ ...summary, unreadCount: 0, byCategory: { ...summary.byCategory, MOODLE: 0, GRADES: 0 } }),
      notifications: queryResult([]),
    })

    renderPage()

    expect(screen.getByText('No notifications found')).toBeInTheDocument()
    expect(screen.getByText('You are all caught up.')).toBeInTheDocument()
  })

  it('renders loading and error states safely', () => {
    setDefaultHookState({
      summary: queryResult(undefined, { isLoading: true }),
      notifications: queryResult(undefined, { isError: true }),
    })

    renderPage()

    expect(screen.getByText('Loading notifications')).toBeInTheDocument()
    expect(screen.getByText('Could not load notifications')).toBeInTheDocument()
    expect(screen.getByText('Check your connection and session.')).toBeInTheDocument()
  })
})
