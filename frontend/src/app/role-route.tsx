import { Outlet } from 'react-router-dom'

import type { PrimaryRole } from '@/api/contracts'
import { ForbiddenPage } from '@/pages/forbidden-page'
import { useAuth } from '@/auth/auth-context'

export function RoleRoute({ allowedRoles }: { allowedRoles: PrimaryRole[] }) {
  const { session } = useAuth()

  if (!session) {
    return null
  }

  if (!allowedRoles.includes(session.user.primaryRole)) {
    return <ForbiddenPage />
  }

  return <Outlet />
}
