import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { Sidebar } from '@/components/layout/Sidebar'
import { AppRouter } from '@/router'
import { useAuthStore } from '@/stores/authStore'
import type { AuthenticatedUser, PrimaryRole } from '@/types'

vi.mock('@/pages/admin/AIFoundation', () => ({
  AdminAIFoundationPage: () => <div>AI foundation route page</div>,
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

describe('AI foundation route and navigation', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
  })

  it('registers /admin/ai-foundation for admins with the AppShell heading', () => {
    setSession('ADMIN')

    render(
      <MemoryRouter initialEntries={['/admin/ai-foundation']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByText('AI foundation route page')).toBeInTheDocument()
    expect(screen.getByText('AI foundation route page')).toBeInTheDocument()
    expect(screen.getByText('Monitor analytics ETL, vector-store readiness, and institutional knowledge retrieval.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /AI Foundation/i })).toBeInTheDocument()
    expect(screen.getByText('AI foundation route page')).toBeInTheDocument()
    expect(screen.getAllByText('AI Foundation')).toHaveLength(2)
  })

  it('denies /admin/ai-foundation for non-admin users', () => {
    setSession('STUDENT')

    render(
      <MemoryRouter initialEntries={['/admin/ai-foundation']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Access denied' })).toBeInTheDocument()
    expect(screen.getByText('Requested route: /admin/ai-foundation')).toBeInTheDocument()
  })

  it('shows AI Foundation in the admin sidebar only', () => {
    setSession('ADMIN')
    const { unmount } = render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.getByText('Insights')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /AI Foundation/i })).toHaveAttribute('href', '/admin/ai-foundation')
    unmount()

    setSession('STUDENT')
    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.queryByRole('link', { name: /AI Foundation/i })).not.toBeInTheDocument()
  })
})
