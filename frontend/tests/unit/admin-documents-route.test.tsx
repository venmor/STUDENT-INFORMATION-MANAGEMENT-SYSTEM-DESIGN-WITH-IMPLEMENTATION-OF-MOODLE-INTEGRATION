import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { Sidebar } from '@/components/layout/Sidebar'
import { AppRouter } from '@/router'
import { useAuthStore } from '@/stores/authStore'
import type { AuthenticatedUser, PrimaryRole } from '@/types'

vi.mock('@/pages/admin/Documents', () => ({
  AdminDocumentsPage: () => <div>Admin documents route page</div>,
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

describe('admin documents route and navigation', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
  })

  it('registers /admin/documents for admins with the AppShell heading', () => {
    setSession('ADMIN')

    render(
      <MemoryRouter initialEntries={['/admin/documents']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByText('Admin documents route page')).toBeInTheDocument()
    expect(screen.getByText('Student Documents')).toBeInTheDocument()
    expect(screen.getByText('Review, classify, and protect student-linked institutional documents.')).toBeInTheDocument()
  })

  it('denies /admin/documents for non-admin users', () => {
    setSession('STUDENT')

    render(
      <MemoryRouter initialEntries={['/admin/documents']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Access denied' })).toBeInTheDocument()
    expect(screen.getByText('Requested route: /admin/documents')).toBeInTheDocument()
  })

  it('shows Documents in the admin sidebar under Academic Operations', () => {
    setSession('ADMIN')

    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.getByText('Academic Operations')).toBeInTheDocument()
    const documentsLink = screen.getByRole('link', { name: /Documents/i })
    expect(documentsLink).toHaveAttribute('href', '/admin/documents')

    const navText = screen.getByRole('navigation').textContent ?? ''
    expect(navText.indexOf('Academic Calendar')).toBeLessThan(navText.indexOf('Documents'))
    expect(navText.indexOf('Documents')).toBeLessThan(navText.indexOf('Moodle Sync'))
  })
})
