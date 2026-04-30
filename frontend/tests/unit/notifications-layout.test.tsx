import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'
import { AppRouter } from '@/router'
import { useAuthStore } from '@/stores/authStore'
import type { AuthenticatedUser } from '@/types'

const mocks = vi.hoisted(() => ({
  summary: {
    data: {
      unreadCount: 4,
      byCategory: {
        ACADEMIC: 0,
        MOODLE: 1,
        GRADES: 1,
        ENROLLMENT: 1,
        ADVISING: 1,
        SYSTEM: 0,
      },
      latest: [],
    },
    isLoading: false,
    isError: false,
  },
}))

vi.mock('@/hooks/useNotifications', () => ({
  useNotificationSummary: () => mocks.summary,
}))

vi.mock('@/pages/Notifications', () => ({
  NotificationsPage: () => <div>Notifications route page</div>,
}))

function setSession(overrides?: Partial<AuthenticatedUser>) {
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

describe('notification route and layout polish', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
    setSession()
  })

  it('registers the /notifications route for authenticated users', () => {
    render(
      <MemoryRouter
        initialEntries={['/notifications']}
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <AppRouter />
      </MemoryRouter>,
    )

    expect(screen.getByText('Notifications route page')).toBeInTheDocument()
    expect(screen.getByText('Notifications')).toBeInTheDocument()
    expect(screen.getByText('Review academic, Moodle, grades, enrollment, advising, and system updates.')).toBeInTheDocument()
  })

  it('shows grouped admin sidebar navigation with Moodle Sync in the required order', () => {
    render(
      <MemoryRouter
        initialEntries={['/admin/moodle-sync']}
        future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
      >
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.getByText('Overview')).toBeInTheDocument()
    expect(screen.getByText('Academic Operations')).toBeInTheDocument()
    expect(screen.getByText('Integrations')).toBeInTheDocument()
    expect(screen.getByText('Governance')).toBeInTheDocument()

    const moodleSyncLink = screen.getByRole('link', { name: /Moodle Sync/i })
    expect(moodleSyncLink).toHaveAttribute('href', '/admin/moodle-sync')
    expect(moodleSyncLink).toHaveAttribute('aria-current', 'page')
    expect(moodleSyncLink.className).toContain('bg-white')

    const navText = screen.getByRole('navigation').textContent ?? ''
    expect(navText.indexOf('Courses')).toBeLessThan(navText.indexOf('Moodle Sync'))
    expect(navText.indexOf('Moodle Sync')).toBeLessThan(navText.indexOf('Audit Log'))
  })

  it('moves sign out into the sidebar and keeps password access in the account card', () => {
    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Sidebar />
      </MemoryRouter>,
    )

    expect(screen.getByText('Admin One')).toBeInTheDocument()
    expect(screen.getByText('ADMIN')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Password/i })).toHaveAttribute('href', '/account/password')
    expect(screen.getByRole('button', { name: /Sign out/i })).toBeInTheDocument()
  })

  it('renders a topbar notification bell with unread count and no sign out button', () => {
    const { container } = render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <Topbar title="Notifications" subtitle="Review academic, Moodle, grades, enrollment, advising, and system updates." />
      </MemoryRouter>,
    )

    expect(screen.getByRole('link', { name: /Notifications/i })).toHaveAttribute('href', '/notifications')
    expect(screen.getByText('4')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Sign out/i })).not.toBeInTheDocument()
    expect(container.textContent).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u)
  })
})
