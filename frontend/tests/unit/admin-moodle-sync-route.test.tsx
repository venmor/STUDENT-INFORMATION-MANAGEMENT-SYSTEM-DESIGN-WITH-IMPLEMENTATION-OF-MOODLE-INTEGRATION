import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { Sidebar } from '@/components/layout/Sidebar'
import { AppRouter } from '@/router'
import { useAuthStore } from '@/stores/authStore'
import type { AuthenticatedUser } from '@/types'

vi.mock('@/pages/admin/MoodleSync', () => ({
  AdminMoodleSyncPage: () => <div>Moodle Sync route page</div>,
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

describe('admin Moodle sync route and navigation', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
    setAdminSession()
  })

  it('registers the /admin/moodle-sync route for admins', () => {
    render(
      <MemoryRouter
        initialEntries={['/admin/moodle-sync']}
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByText('Moodle Sync route page')).toBeInTheDocument()
  })

  it('shows Moodle Sync in the admin sidebar after Courses and before Audit Log', () => {
    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    const moodleSyncLink = screen.getByRole('link', { name: /Moodle Sync/i })
    expect(moodleSyncLink).toHaveAttribute('href', '/admin/moodle-sync')

    const navText = screen.getByRole('navigation').textContent ?? ''
    expect(navText.indexOf('Courses')).toBeLessThan(navText.indexOf('Moodle Sync'))
    expect(navText.indexOf('Moodle Sync')).toBeLessThan(navText.indexOf('Audit Log'))
  })
})
