import {
  AcademicCapIcon,
  ArrowPathIcon,
  ArrowRightOnRectangleIcon,
  CalendarDaysIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  ClipboardDocumentCheckIcon,
  CpuChipIcon,
  DocumentTextIcon,
  HeartIcon,
  HomeIcon,
  IdentificationIcon,
  KeyIcon,
  RectangleStackIcon,
  ShieldCheckIcon,
  Squares2X2Icon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'
import { Link, NavLink } from 'react-router-dom'

import { Button } from '@/components/ui/Button'
import { useAuth } from '@/hooks/useAuth'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import type { PrimaryRole } from '@/types'
import { cn } from '@/utils/cn'

type NavigationItem = { label: string; icon: typeof HomeIcon; to: string }
type NavigationGroup = { label: string; items: NavigationItem[] }

const navigationGroupsByRole: Record<PrimaryRole, NavigationGroup[]> = {
  STUDENT: [
    {
      label: 'Student',
      items: [
        { label: 'Dashboard', icon: Squares2X2Icon, to: '/student' },
        { label: 'My Courses', icon: RectangleStackIcon, to: '/student/courses' },
        { label: 'My Grades', icon: ClipboardDocumentCheckIcon, to: '/student/grades' },
        { label: 'Registration', icon: IdentificationIcon, to: '/student/register' },
        { label: 'AI Co-pilot', icon: ChatBubbleLeftRightIcon, to: '/student/copilot' },
        { label: 'Academic Calendar', icon: CalendarDaysIcon, to: '/calendar' },
        { label: 'Documents', icon: DocumentTextIcon, to: '/documents' },
        { label: 'Corrections', icon: UserGroupIcon, to: '/student/corrections' },
        { label: 'Wellbeing', icon: HeartIcon, to: '/student/wellbeing' },
      ],
    },
  ],
  ADVISOR: [
    {
      label: 'Advising',
      items: [
        { label: 'Dashboard', icon: Squares2X2Icon, to: '/advisor' },
        { label: 'Registrations', icon: ClipboardDocumentCheckIcon, to: '/advisor/registrations' },
        { label: 'Academic Calendar', icon: CalendarDaysIcon, to: '/calendar' },
        { label: 'Alert History', icon: ShieldCheckIcon, to: '/advisor/alerts' },
      ],
    },
  ],
  FACULTY: [
    {
      label: 'Teaching',
      items: [
        { label: 'Dashboard', icon: Squares2X2Icon, to: '/faculty' },
        { label: 'Academic Calendar', icon: CalendarDaysIcon, to: '/calendar' },
      ],
    },
  ],
  ADMIN: [
    {
      label: 'Overview',
      items: [{ label: 'Dashboard', icon: Squares2X2Icon, to: '/admin' }],
    },
    {
      label: 'Academic Operations',
      items: [
        { label: 'Users', icon: UserGroupIcon, to: '/admin/users' },
        { label: 'Courses', icon: RectangleStackIcon, to: '/admin/courses' },
        { label: 'Structure', icon: AcademicCapIcon, to: '/admin/academic-structure' },
        { label: 'Admissions', icon: IdentificationIcon, to: '/admin/admissions' },
        { label: 'Academic Calendar', icon: CalendarDaysIcon, to: '/calendar' },
        { label: 'Documents', icon: DocumentTextIcon, to: '/admin/documents' },
      ],
    },
    {
      label: 'Integrations',
      items: [{ label: 'Moodle Sync', icon: ArrowPathIcon, to: '/admin/moodle-sync' }],
    },
    {
      label: 'Governance',
      items: [{ label: 'Audit Log', icon: ClipboardDocumentCheckIcon, to: '/admin/audit-log' }],
    },
    {
      label: 'Insights',
      items: [
        { label: 'Reports', icon: ChartBarIcon, to: '/admin/reports' },
        { label: 'AI Foundation', icon: CpuChipIcon, to: '/admin/ai-foundation' },
        { label: 'Summarise', icon: DocumentTextIcon, to: '/admin/summarise' },
      ],
    },
  ],
}

export function Sidebar({
  mobile = false,
}: {
  mobile?: boolean
}) {
  const { logout } = useAuth()
  const user = useCurrentUser()

  if (!user) {
    return null
  }

  return (
    <aside
      className={cn(
        'shrink-0 bg-primary text-white',
        mobile ? 'flex h-full w-full flex-col' : 'hidden h-screen w-64 shrink-0 border-r border-neutral-200 lg:flex lg:flex-col',
      )}
    >
      <div className={cn('items-center border-b border-white/10 px-6', mobile ? 'hidden' : 'flex h-16')}>
        <div className="flex items-center gap-3">
          <img src="/sis-logo.svg" alt="" className="h-10 w-10" />
          <div>
            <p className="font-display text-lg font-bold">Student Information System</p>
            <p className="text-sm text-blue-100">Academic records and operations</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-4">
        {navigationGroupsByRole[user.primaryRole].map((group) => (
          <div key={group.label}>
            <p className="px-3 text-xs font-semibold uppercase tracking-[0.18em] text-blue-100/80">{group.label}</p>
            <div className="mt-2 space-y-1">
              {group.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === `/${user.primaryRole.toLowerCase()}`}
                  className={({ isActive }) =>
                    cn(
                      'group relative flex min-h-11 items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors',
                      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/80 focus-visible:ring-offset-2 focus-visible:ring-offset-primary',
                      isActive ? 'bg-white/16 text-white shadow-sm' : 'text-blue-100 hover:bg-white/10 hover:text-white',
                    )
                  }
                >
                  {({ isActive }) => (
                    <>
                      <span
                        className={cn(
                          'absolute bottom-2 left-0 top-2 w-1 rounded-r-full transition-colors',
                          isActive ? 'bg-secondary' : 'bg-transparent',
                        )}
                      />
                      <span
                        className={cn(
                          'flex h-8 w-8 items-center justify-center rounded-lg transition-colors',
                          isActive ? 'bg-white text-primary' : 'bg-white/8 text-blue-100 group-hover:bg-white/14 group-hover:text-white',
                        )}
                      >
                        <item.icon className="h-5 w-5" />
                      </span>
                      <span>{item.label}</span>
                    </>
                  )}
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>
      <div className="border-t border-white/10 p-3">
        <div className="rounded-2xl border border-white/10 bg-white/8 p-4 text-sm text-blue-100">
          <p className="truncate font-semibold text-white">{user.fullName || user.username}</p>
          <p className="mt-1 font-mono text-xs uppercase tracking-[0.18em]">{user.primaryRole}</p>
          <Link
            to="/account/password"
            className="mt-3 inline-flex min-h-11 w-full items-center gap-2 rounded-lg px-3 text-sm font-semibold text-blue-100 transition-colors hover:bg-white/10 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/80 focus-visible:ring-offset-2 focus-visible:ring-offset-primary"
          >
            <KeyIcon className="h-4 w-4" />
            Password
          </Link>
        </div>
        <Button
          variant="ghost"
          className="mt-3 w-full justify-start text-blue-100 hover:bg-white/10 hover:text-white"
          onClick={logout}
        >
          <ArrowRightOnRectangleIcon className="h-5 w-5" />
          Sign out
        </Button>
      </div>
    </aside>
  )
}
