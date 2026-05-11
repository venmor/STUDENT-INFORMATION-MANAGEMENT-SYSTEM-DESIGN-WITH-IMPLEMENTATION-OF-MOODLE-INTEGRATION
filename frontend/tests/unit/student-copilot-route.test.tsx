import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { Sidebar } from '@/components/layout/Sidebar'
import { AppRouter } from '@/router'
import { useAuthStore } from '@/stores/authStore'
import type { AuthenticatedUser, PrimaryRole } from '@/types'

vi.mock('@/pages/student/Copilot', () => ({
  StudentCopilotPage: () => <div>student copilot route page</div>,
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

describe('student co-pilot route and navigation', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
  })

  it('registers /student/copilot with the AppShell heading for students', () => {
    setSession('STUDENT')

    render(
      <MemoryRouter initialEntries={['/student/copilot']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByText('student copilot route page')).toBeInTheDocument()
    expect(screen.getAllByText('AI Co-pilot')).toHaveLength(2)
    expect(screen.getByText('Ask questions about registration, deadlines, courses, documents, and academic rules.')).toBeInTheDocument()
  })

  it('denies /student/copilot for non-students', () => {
    setSession('ADVISOR')

    render(
      <MemoryRouter initialEntries={['/student/copilot']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Access denied' })).toBeInTheDocument()
    expect(screen.getByText('Requested route: /student/copilot')).toBeInTheDocument()
  })

  it('shows AI Co-pilot in the student sidebar only', () => {
    setSession('STUDENT')
    const { unmount } = render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.getByRole('link', { name: /AI Co-pilot/i })).toHaveAttribute('href', '/student/copilot')
    unmount()

    setSession('ADMIN')
    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.queryByRole('link', { name: /AI Co-pilot/i })).not.toBeInTheDocument()
  })
})
