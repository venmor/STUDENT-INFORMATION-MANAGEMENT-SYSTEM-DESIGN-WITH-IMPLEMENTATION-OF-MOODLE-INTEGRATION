import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import { AppProviders } from '@/app/app-providers'
import { AppRoutes } from '@/app/app-routes'
import type { Session } from '@/auth/auth-storage'

function renderAt(pathname: string, session: Session | null = null) {
  return render(
    <AppProviders initialSession={session}>
      <MemoryRouter initialEntries={[pathname]}>
        <AppRoutes />
      </MemoryRouter>
    </AppProviders>,
  )
}

describe('App route protection', () => {
  it('redirects unauthenticated users to the login page', async () => {
    renderAt('/student/overview')

    expect(await screen.findByRole('heading', { name: /modern sis access/i })).toBeInTheDocument()
  })

  it('shows a forbidden screen for authenticated users on the wrong role route', async () => {
    renderAt('/student/overview', {
      accessToken: 'token',
      refreshToken: 'refresh',
      expiresAt: Date.now() + 60_000,
      user: {
        id: 9,
        username: 'advisor1',
        fullName: 'Advisor One',
        primaryRole: 'ADVISOR',
        mustResetPassword: false,
        studentProfileId: null,
      },
    })

    expect(
      await screen.findByRole('heading', {
        name: /^forbidden$/i,
      }),
    ).toBeInTheDocument()
  })
})
