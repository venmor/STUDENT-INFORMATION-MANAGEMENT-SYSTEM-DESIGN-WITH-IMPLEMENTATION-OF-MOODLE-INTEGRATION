import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { useAuthStore } from '@/stores/authStore'
import type { AuthenticatedUser } from '@/types'

function ProtectedRouteHarness({
  allowedRoles,
  initialPath = '/protected',
}: {
  allowedRoles: Array<'STUDENT' | 'ADVISOR' | 'FACULTY' | 'ADMIN'>
  initialPath?: string
}) {
  return (
    <MemoryRouter
      initialEntries={[initialPath]}
      future={{ v7_relativeSplatPath: true, v7_startTransition: true }}
    >
      <Routes>
        <Route path="/login" element={<div>Login page</div>} />
        <Route
          path="/protected"
          element={
            <ProtectedRoute allowedRoles={allowedRoles}>
              <div>Allowed content</div>
            </ProtectedRoute>
          }
        />
        <Route path="/account/password" element={<div>Password page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

function setSession(overrides?: Partial<AuthenticatedUser>) {
  useAuthStore.getState().setSession({
    accessToken: 'access-token',
    refreshToken: 'refresh-token',
    expiresAt: Date.now() + 1000 * 60 * 15,
    user: {
      id: 9,
      username: 'advisor.one',
      fullName: 'Advisor One',
      primaryRole: 'ADVISOR',
      mustResetPassword: false,
      studentProfileId: null,
      ...overrides,
    },
  })
}

describe('ProtectedRoute', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
  })

  it('redirects unauthenticated users to the login page', () => {
    render(<ProtectedRouteHarness allowedRoles={['STUDENT']} />)

    expect(screen.getByText('Login page')).toBeInTheDocument()
  })

  it('renders the access denied state for a wrong-role user', () => {
    setSession()

    render(<ProtectedRouteHarness allowedRoles={['STUDENT']} />)

    expect(screen.getByRole('heading', { name: 'Access denied' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Go to advisor dashboard' })).toHaveAttribute('href', '/advisor')
  })

  it('redirects password-reset users to the password page', () => {
    setSession({ mustResetPassword: true })

    render(<ProtectedRouteHarness allowedRoles={['ADVISOR']} />)

    expect(screen.getByText('Password page')).toBeInTheDocument()
  })
})
