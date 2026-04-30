import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { Sidebar } from '@/components/layout/Sidebar'
import { AppRouter } from '@/router'
import { useAuthStore } from '@/stores/authStore'
import type { AuthenticatedUser, PrimaryRole } from '@/types'

vi.mock('@/pages/admin/Reports', () => ({
  AdminReportsPage: () => <div>Reports route page</div>,
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

describe('admin reports route and navigation', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
  })

  it('registers /admin/reports for admins with the AppShell heading', () => {
    setSession('ADMIN')

    render(
      <MemoryRouter initialEntries={['/admin/reports']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByText('Reports route page')).toBeInTheDocument()
    expect(screen.getByText('Institution Reports')).toBeInTheDocument()
    expect(
      screen.getByText('Monitor enrollment, capacity, grades, Moodle health, deadlines, and operational activity.'),
    ).toBeInTheDocument()
  })

  it('denies /admin/reports for non-admin users', () => {
    setSession('STUDENT')

    render(
      <MemoryRouter initialEntries={['/admin/reports']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Access denied' })).toBeInTheDocument()
    expect(screen.getByText('Requested route: /admin/reports')).toBeInTheDocument()
  })

  it('shows Reports in the admin sidebar under Insights after Audit Log', () => {
    setSession('ADMIN')

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.getByText('Insights')).toBeInTheDocument()
    const reportsLink = screen.getByRole('link', { name: /Reports/i })
    expect(reportsLink).toHaveAttribute('href', '/admin/reports')

    const navText = screen.getByRole('navigation').textContent ?? ''
    expect(navText.indexOf('Audit Log')).toBeLessThan(navText.indexOf('Reports'))
  })
})
