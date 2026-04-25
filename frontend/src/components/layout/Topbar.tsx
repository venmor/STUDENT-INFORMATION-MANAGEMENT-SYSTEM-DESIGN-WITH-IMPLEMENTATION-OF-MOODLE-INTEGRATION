import { ArrowRightOnRectangleIcon, KeyIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/Button'
import { useAuth } from '@/hooks/useAuth'
import { useCurrentUser } from '@/hooks/useCurrentUser'

export function Topbar({ title, subtitle }: { title: string; subtitle: string }) {
  const { logout } = useAuth()
  const user = useCurrentUser()

  return (
    <header className="sticky top-0 z-20 border-b border-neutral-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-page items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <div className="min-w-0">
          <p className="truncate font-display text-2xl font-bold text-neutral-900">{title}</p>
          <p className="truncate text-sm text-neutral-500">{subtitle}</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="hidden rounded-xl border border-neutral-200 bg-neutral-50 px-3 py-2 text-right sm:block">
            <p className="text-sm font-medium text-neutral-900">{user?.fullName}</p>
            <p className="font-mono text-xs uppercase tracking-wide text-neutral-500">{user?.primaryRole}</p>
          </div>
          <Link
            to="/account/password"
            className="inline-flex min-h-11 min-w-[7rem] items-center justify-center gap-2 rounded-lg px-3 text-sm font-semibold text-neutral-600 transition-colors duration-150 hover:bg-neutral-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2"
          >
            <KeyIcon className="h-4 w-4" />
            Password
          </Link>
          <Button variant="ghost" size="sm" className="min-w-0 px-3" onClick={logout}>
            <ArrowRightOnRectangleIcon className="h-4 w-4" />
            Sign out
          </Button>
        </div>
      </div>
    </header>
  )
}
