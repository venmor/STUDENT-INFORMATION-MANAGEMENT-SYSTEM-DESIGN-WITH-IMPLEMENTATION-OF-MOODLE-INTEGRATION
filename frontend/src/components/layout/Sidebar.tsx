import { ArrowPathIcon, Bars3Icon, ClipboardDocumentCheckIcon, HomeIcon, IdentificationIcon, RectangleStackIcon, ShieldCheckIcon, Squares2X2Icon, UserGroupIcon } from '@heroicons/react/24/outline'
import { NavLink } from 'react-router-dom'

import { Button } from '@/components/ui/Button'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import type { PrimaryRole } from '@/types'
import { cn } from '@/utils/cn'

const navigationByRole: Record<
  PrimaryRole,
  Array<{ label: string; icon: typeof HomeIcon; to: string }>
> = {
  STUDENT: [
    { label: 'Dashboard', icon: Squares2X2Icon, to: '/student' },
    { label: 'My Courses', icon: RectangleStackIcon, to: '/student/courses' },
    { label: 'My Grades', icon: ClipboardDocumentCheckIcon, to: '/student/grades' },
    { label: 'Registration', icon: IdentificationIcon, to: '/student/register' },
    { label: 'Corrections', icon: UserGroupIcon, to: '/student/corrections' },
  ],
  ADVISOR: [
    { label: 'Dashboard', icon: Squares2X2Icon, to: '/advisor' },
    { label: 'Alert History', icon: ShieldCheckIcon, to: '/advisor/alerts' },
  ],
  FACULTY: [
    { label: 'Dashboard', icon: Squares2X2Icon, to: '/faculty' },
  ],
  ADMIN: [
    { label: 'Dashboard', icon: Squares2X2Icon, to: '/admin' },
    { label: 'Users', icon: UserGroupIcon, to: '/admin/users' },
    { label: 'Courses', icon: RectangleStackIcon, to: '/admin/courses' },
    { label: 'Moodle Sync', icon: ArrowPathIcon, to: '/admin/moodle-sync' },
    { label: 'Audit Log', icon: ClipboardDocumentCheckIcon, to: '/admin/audit-log' },
  ],
}

export function Sidebar({
  mobile = false,
  onOpenMobile,
}: {
  mobile?: boolean
  onOpenMobile?: () => void
}) {
  const user = useCurrentUser()

  if (!user) {
    return null
  }

  return (
    <aside
      className={cn(
        'w-64 shrink-0 bg-primary text-white',
        mobile ? 'flex h-full flex-col' : 'hidden border-r border-neutral-200 lg:flex lg:flex-col',
      )}
    >
      <div className="flex h-16 items-center border-b border-white/10 px-6">
        <div className="flex items-center gap-3">
          <img src="/sis-logo.svg" alt="" className="h-10 w-10" />
          <div>
            <p className="font-display text-lg font-bold">Student Information System</p>
            <p className="text-sm text-blue-100">Academic records and operations</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigationByRole[user.primaryRole].map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === `/${user.primaryRole.toLowerCase()}`}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-colors',
                isActive ? 'bg-white/14 text-white' : 'text-blue-100 hover:bg-white/8 hover:text-white',
              )
            }
          >
            <item.icon className="h-5 w-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="mx-3 mb-3 rounded-2xl border border-white/10 bg-white/8 p-4 text-sm text-blue-100">
        <p className="font-semibold text-white">Current role</p>
        <p className="mt-1 font-mono text-xs uppercase tracking-[0.2em]">{user.primaryRole}</p>
      </div>
      {onOpenMobile ? (
        <div className="border-t border-white/10 p-3 lg:hidden">
          <Button variant="ghost" onClick={onOpenMobile} className="w-full justify-start text-white hover:bg-white/10">
            <Bars3Icon className="h-5 w-5" />
            Menu
          </Button>
        </div>
      ) : null}
    </aside>
  )
}
