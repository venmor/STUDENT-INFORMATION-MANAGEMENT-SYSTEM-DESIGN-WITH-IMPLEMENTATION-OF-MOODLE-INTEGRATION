import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { Sidebar } from '@/components/layout/Sidebar'
import { AppRouter } from '@/router'
import { useAuthStore } from '@/stores/authStore'
import type { AuthenticatedUser, PrimaryRole } from '@/types'

vi.mock('@/pages/student/Documents', () => ({
  StudentDocumentsPage: () => <div>Student documents route page</div>,
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

describe('student documents route and navigation', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
  })

  it('registers /documents for students with the AppShell heading', () => {
    setSession('STUDENT')

    render(
      <MemoryRouter initialEntries={['/documents']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByText('Student documents route page')).toBeInTheDocument()
    expect(screen.getByText('My Documents')).toBeInTheDocument()
    expect(screen.getByText('View documents shared with you and upload supporting files when allowed.')).toBeInTheDocument()
  })

  it('denies /documents for non-student users', () => {
    setSession('FACULTY')

    render(
      <MemoryRouter initialEntries={['/documents']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Access denied' })).toBeInTheDocument()
    expect(screen.getByText('Requested route: /documents')).toBeInTheDocument()
  })

  it('shows Documents in the student sidebar and hides it for faculty', () => {
    setSession('STUDENT')

    const { unmount } = render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.getByRole('link', { name: /Documents/i })).toHaveAttribute('href', '/documents')
    unmount()

    useAuthStore.getState().logout()
    setSession('FACULTY')

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.queryByRole('link', { name: /Documents/i })).not.toBeInTheDocument()
  })
})
