import type { ReactNode } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { AccessDeniedPage } from '@/pages/AccessDenied'
import { useAuthStore } from '@/stores/authStore'
import type { PrimaryRole } from '@/types'
import { roleHomePath } from '@/utils/roleGuards'

export function ProtectedRoute({
  allowedRoles,
  children,
}: {
  allowedRoles: PrimaryRole[]
  children?: ReactNode
}) {
  const session = useAuthStore((state) => state.session)
  const location = useLocation()

  if (!session) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (session.user.mustResetPassword && location.pathname !== '/account/password') {
    return <Navigate to="/account/password" replace />
  }

  if (!allowedRoles.includes(session.user.primaryRole)) {
    return (
      <AccessDeniedPage
        attemptedPath={location.pathname}
        homePath={roleHomePath(session.user.primaryRole)}
        role={session.user.primaryRole}
      />
    )
  }

  return <>{children ?? <Outlet />}</>
}
