import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

import { Card } from '@/components/ui/Card'
import { cn } from '@/utils/cn'
import type { PrimaryRole } from '@/types'

export function AccessDeniedPage({
  attemptedPath,
  homePath,
  role,
}: {
  attemptedPath?: string
  homePath?: string
  role?: PrimaryRole
}) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="max-w-lg text-center">
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-danger" />
        <h1 className="mt-4 text-2xl font-semibold text-neutral-900">Access denied</h1>
        <p className="mt-2 text-sm text-neutral-500">
          Your account is authenticated, but this route is not available to your assigned role.
        </p>
        {attemptedPath ? (
          <p className="mt-3 font-mono text-xs text-neutral-500">Requested route: {attemptedPath}</p>
        ) : null}
        {homePath && role ? (
          <div className="mt-6 flex justify-center">
            <Link
              to={homePath}
              className={cn(
                'inline-flex min-h-11 min-w-[10rem] items-center justify-center rounded-lg bg-primary px-4 text-sm font-semibold text-white transition-colors duration-150 hover:bg-primary-dark',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2',
              )}
            >
              Go to {role.toLowerCase()} dashboard
            </Link>
          </div>
        ) : null}
      </Card>
    </div>
  )
}
