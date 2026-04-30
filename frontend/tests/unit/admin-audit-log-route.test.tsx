import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { Sidebar } from '@/components/layout/Sidebar'
import { AppRouter } from '@/router'
import { useAuthStore } from '@/stores/authStore'
import type { AuthenticatedUser } from '@/types'

vi.mock('@/pages/admin/AuditLog', () => ({
  AdminAuditLogPage: () => <div>Audit Log route page</div>,
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

function setAdminSession(overrides?: Partial<AuthenticatedUser>) {
  useAuthStore.getState().setSession({
    accessToken: 'access-token',
    refreshToken: 'refresh-token',
    expiresAt: Date.now() + 1000 * 60 * 15,
    user: {
      id: 1,
      username: 'admin.one',
      fullName: 'Admin One',
      primaryRole: 'ADMIN',
      mustResetPassword: false,
      studentProfileId: null,
      ...overrides,
    },
  })
}

describe('admin audit log route and navigation', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
    setAdminSession()
  })

  it('registers the /admin/audit-log route for admins', () => {
    render(
      <MemoryRouter
        initialEntries={['/admin/audit-log']}
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByText('Audit Log route page')).toBeInTheDocument()
  })

  it('keeps Audit Log in the admin sidebar governance section', () => {
    render(
      <MemoryRouter initialEntries={['/admin/audit-log']} future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.getByText('Governance')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Audit Log/i })).toHaveAttribute('href', '/admin/audit-log')
  })
})
