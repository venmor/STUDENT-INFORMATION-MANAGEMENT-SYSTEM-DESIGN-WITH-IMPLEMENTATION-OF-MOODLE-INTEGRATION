import { BellIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

import { useCurrentUser } from '@/hooks/useCurrentUser'
import { useNotificationSummary } from '@/hooks/useNotifications'

export function Topbar({ title, subtitle }: { title: string; subtitle: string }) {
  const user = useCurrentUser()
  const summaryQuery = useNotificationSummary()
  const unreadCount = summaryQuery.data?.unreadCount ?? 0
  const unreadLabel = unreadCount > 99 ? '99+' : String(unreadCount)

  return (
    <header className="sticky top-0 z-20 border-b border-neutral-200 bg-white/90 shadow-sm backdrop-blur">
      <div className="mx-auto flex h-16 max-w-page items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <div className="min-w-0">
          <p className="truncate font-display text-2xl font-bold text-neutral-900">{title}</p>
          <p className="truncate text-sm text-neutral-500">{subtitle}</p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/notifications"
            aria-label="Notifications"
            className="relative inline-flex min-h-11 min-w-11 items-center justify-center rounded-lg border border-neutral-200 bg-white text-neutral-600 transition-colors hover:bg-neutral-50 hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2"
          >
            <BellIcon className="h-5 w-5" />
            {unreadCount > 0 ? (
              <span className="absolute -right-1 -top-1 inline-flex min-h-5 min-w-5 items-center justify-center rounded-full bg-danger px-1.5 text-xs font-semibold text-white">
                {unreadLabel}
              </span>
            ) : null}
          </Link>
          <div className="hidden rounded-xl border border-neutral-200 bg-neutral-50 px-3 py-2 text-right sm:block">
            <p className="text-sm font-medium text-neutral-900">{user?.fullName}</p>
            <p className="font-mono text-xs uppercase tracking-wide text-neutral-500">{user?.primaryRole}</p>
          </div>
        </div>
      </div>
    </header>
  )
}
