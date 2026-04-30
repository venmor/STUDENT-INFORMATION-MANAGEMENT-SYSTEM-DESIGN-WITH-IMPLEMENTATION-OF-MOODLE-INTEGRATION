import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { Sidebar } from '@/components/layout/Sidebar'
import { AppRouter } from '@/router'
import { useAuthStore } from '@/stores/authStore'
import type { AuthenticatedUser, PrimaryRole } from '@/types'

vi.mock('@/pages/AcademicCalendar', () => ({
  AcademicCalendarPage: () => <div>Academic Calendar route page</div>,
}))

vi.mock('@/hooks/useNotifications', () => ({
  useNotificationSummary: () => ({
    data: {
      unreadCount: 0,
      latest: [],
      byCategory: {
        ACADEMIC: 0,
        MOODLE: 0,
        GRADES: 0,
        ENROLLMENT: 0,
        ADVISING: 0,
        SYSTEM: 0,
      },
    },
    isLoading: false,
    isError: false,
  }),
}))

function setSession(primaryRole: PrimaryRole, overrides?: Partial<AuthenticatedUser>) {
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
      ...overrides,
    },
  })
}

describe('academic calendar route and navigation', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
  })

  it.each<PrimaryRole>(['STUDENT', 'ADVISOR', 'FACULTY', 'ADMIN'])('registers /calendar for %s users', (role) => {
    setSession(role)

    render(
      <MemoryRouter initialEntries={['/calendar']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByText('Academic Calendar route page')).toBeInTheDocument()
    expect(screen.getAllByText('Academic Calendar').length).toBeGreaterThan(0)
    expect(screen.getByText('Track registration, deadlines, exam periods, and academic milestones.')).toBeInTheDocument()
  })

  it.each<PrimaryRole>(['STUDENT', 'ADVISOR', 'FACULTY', 'ADMIN'])('shows Academic Calendar in the %s sidebar', (role) => {
    setSession(role)

    render(
      <MemoryRouter initialEntries={['/calendar']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.getByRole('link', { name: /Academic Calendar/i })).toHaveAttribute('href', '/calendar')
  })

  it('places the student calendar link after Registration and before Corrections', () => {
    setSession('STUDENT')

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    const navText = screen.getByRole('navigation').textContent ?? ''
    expect(navText.indexOf('Registration')).toBeLessThan(navText.indexOf('Academic Calendar'))
    expect(navText.indexOf('Academic Calendar')).toBeLessThan(navText.indexOf('Corrections'))
  })

  it('places the admin calendar link under Academic Operations after Courses', () => {
    setSession('ADMIN')

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.getByText('Academic Operations')).toBeInTheDocument()
    const navText = screen.getByRole('navigation').textContent ?? ''
    expect(navText.indexOf('Courses')).toBeLessThan(navText.indexOf('Academic Calendar'))
    expect(navText.indexOf('Academic Calendar')).toBeLessThan(navText.indexOf('Moodle Sync'))
  })
})
