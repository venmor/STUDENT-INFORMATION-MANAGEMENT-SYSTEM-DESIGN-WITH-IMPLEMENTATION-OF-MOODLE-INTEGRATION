import { fireEvent, render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { AcademicCalendarPage } from '@/pages/AcademicCalendar'
import { useAuthStore } from '@/stores/authStore'
import type { AcademicCalendarEvent, AcademicCalendarSummary } from '@/types/calendar'
import type { PrimaryRole } from '@/types'

const mocks = vi.hoisted(() => ({
  createMutate: vi.fn(),
  updateMutate: vi.fn(),
  cancelMutate: vi.fn(),
  state: {} as Record<string, unknown>,
}))

vi.mock('@/hooks/useAcademicCalendar', () => ({
  useCalendarEvents: () => mocks.state.events,
  useCalendarSummary: () => mocks.state.summary,
  useCreateCalendarEvent: () => mocks.state.createEvent,
  useUpdateCalendarEvent: () => mocks.state.updateEvent,
  useCancelCalendarEvent: () => mocks.state.cancelEvent,
}))

function queryResult(data: unknown, overrides: Record<string, unknown> = {}) {
  return {
    data,
    isLoading: false,
    isError: false,
    ...overrides,
  }
}

const events: AcademicCalendarEvent[] = [
  {
    id: 'event-registration',
    title: 'Registration Deadline',
    description: 'Last day to register for Semester 1 courses.',
    eventType: 'REGISTRATION_DEADLINE',
    audience: 'STUDENTS',
    priority: 'HIGH',
    academicYear: '2026/2027',
    semester: 'Semester 1',
    startAt: '2026-05-15T17:00:00Z',
    endAt: null,
    allDay: false,
    location: 'Registrar Office',
    status: 'ACTIVE',
    source: 'MANUAL',
    relatedCourseSection: null,
    relatedCourseSectionLabel: null,
    urgency: 'UPCOMING',
    metadata: {},
    createdAt: '2026-04-30T12:00:00Z',
    updatedAt: '2026-04-30T12:00:00Z',
  },
  {
    id: 'event-exam',
    title: 'Exam Period',
    description: 'Final examination period.',
    eventType: 'EXAM_PERIOD',
    audience: 'ALL',
    priority: 'HIGH',
    academicYear: '2026/2027',
    semester: 'Semester 1',
    startAt: '2026-05-20T08:00:00Z',
    endAt: '2026-05-25T17:00:00Z',
    allDay: false,
    location: '',
    status: 'ACTIVE',
    source: 'SYSTEM',
    relatedCourseSection: null,
    relatedCourseSectionLabel: null,
    urgency: 'THIS_WEEK',
    metadata: {},
    createdAt: '2026-04-30T12:00:00Z',
    updatedAt: '2026-04-30T12:00:00Z',
  },
]

const summary: AcademicCalendarSummary = {
  upcomingCount: 5,
  registrationDeadlines: 2,
  examPeriods: 1,
  gradeDeadlines: 1,
  currentAcademicYear: '2026/2027',
  currentSemester: 'Semester 1',
  nextEvent: {
    id: 'event-registration',
    title: 'Registration Deadline',
    startAt: '2026-05-15T17:00:00Z',
  },
}

function setSession(primaryRole: PrimaryRole) {
  useAuthStore.getState().setSession({
    accessToken: 'access-token',
    refreshToken: 'refresh-token',
    expiresAt: Date.now() + 1000 * 60 * 15,
    user: {
      id: 1,
      username: `${primaryRole.toLowerCase()}.one`,
      fullName: `${primaryRole} One`,
      primaryRole,
      mustResetPassword: false,
      studentProfileId: primaryRole === 'STUDENT' ? 'student-profile-1' : null,
    },
  })
}

function setDefaultHookState(overrides: Record<string, unknown> = {}) {
  mocks.state = {
    summary: queryResult(summary),
    events: queryResult(events),
    createEvent: {
      mutate: mocks.createMutate,
      isPending: false,
    },
    updateEvent: {
      mutate: mocks.updateMutate,
      isPending: false,
    },
    cancelEvent: {
      mutate: mocks.cancelMutate,
      isPending: false,
    },
    ...overrides,
  }
}

function renderPage(role: PrimaryRole = 'ADMIN') {
  setSession(role)
  return render(
    <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
      <AcademicCalendarPage />
    </MemoryRouter>,
  )
}

describe('AcademicCalendarPage', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
    mocks.createMutate.mockClear()
    mocks.updateMutate.mockClear()
    mocks.cancelMutate.mockClear()
    setDefaultHookState()
  })

  it('renders summary cards, filters, month view, list view controls, My Deadlines, details, and scope without emoji labels', () => {
    const { container } = renderPage()

    expect(screen.getByText('Upcoming Events')).toBeInTheDocument()
    expect(screen.getByText('Registration Deadlines')).toBeInTheDocument()
    expect(screen.getByText('Exam Periods')).toBeInTheDocument()
    expect(screen.getByText('Grade Deadlines')).toBeInTheDocument()
    expect(screen.getByText('Next Event')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'My Deadlines' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Academic Calendar' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Month' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'List' })).toBeInTheDocument()
    expect(screen.getByLabelText('Type')).toBeInTheDocument()
    expect(screen.getByLabelText('Audience')).toBeInTheDocument()
    expect(screen.getByLabelText('Semester')).toBeInTheDocument()
    expect(screen.getByLabelText('Academic Year')).toBeInTheDocument()
    expect(screen.getByLabelText('Status')).toBeInTheDocument()
    expect(screen.getAllByText('Registration Deadline').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Upcoming').length).toBeGreaterThan(0)
    expect(screen.getByRole('heading', { name: 'Event Details' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Current Scope' })).toBeInTheDocument()
    expect(container.textContent).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u)
  })

  it('renders list view events and selectable details', () => {
    renderPage()

    fireEvent.click(screen.getByRole('button', { name: 'List' }))
    fireEvent.click(screen.getAllByRole('button', { name: /Exam Period/i })[0])

    expect(screen.getByText('Final examination period.')).toBeInTheDocument()
    expect(screen.getAllByText('System').length).toBeGreaterThan(0)
  })

  it('shows admin create and cancel controls and calls mutations', () => {
    renderPage('ADMIN')

    fireEvent.click(screen.getByRole('button', { name: 'New Calendar Event' }))
    const dialog = within(screen.getByRole('dialog'))
    fireEvent.change(dialog.getByLabelText('Title'), { target: { value: 'New Deadline' } })
    fireEvent.change(dialog.getByLabelText('Academic Year'), { target: { value: '2026/2027' } })
    fireEvent.change(dialog.getByLabelText('Semester'), { target: { value: 'Semester 1' } })
    fireEvent.change(dialog.getByLabelText('Start date/time'), { target: { value: '2026-05-30T12:00' } })
    fireEvent.click(dialog.getByRole('button', { name: 'Create' }))

    expect(mocks.createMutate).toHaveBeenCalledWith(expect.objectContaining({ title: 'New Deadline' }), expect.any(Object))

    fireEvent.click(dialog.getByRole('button', { name: 'Cancel' }))
    fireEvent.click(screen.getByRole('button', { name: 'Cancel event' }))
    expect(mocks.cancelMutate).toHaveBeenCalledWith('event-registration')
  })

  it('hides admin create controls for non-admin users', () => {
    renderPage('STUDENT')

    expect(screen.queryByRole('button', { name: 'New Calendar Event' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Cancel event' })).not.toBeInTheDocument()
  })

  it('renders role-specific empty states', () => {
    setDefaultHookState({ events: queryResult([]) })
    const { unmount } = renderPage('ADMIN')

    expect(screen.getByText('No academic calendar events found')).toBeInTheDocument()
    expect(screen.getByText('Create an event or seed demo academic dates.')).toBeInTheDocument()
    unmount()

    setDefaultHookState({ events: queryResult([]) })
    renderPage('STUDENT')

    expect(screen.getByText('No academic dates match your current filters.')).toBeInTheDocument()
  })

  it('renders error state', () => {
    setDefaultHookState({
      events: queryResult(undefined, { isError: true }),
    })

    renderPage()

    expect(screen.getByText('Could not load academic calendar')).toBeInTheDocument()
    expect(screen.getByText('Check your connection and session.')).toBeInTheDocument()
  })
})
