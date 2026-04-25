import { useMemo, useState } from 'react'
import { Bars3Icon } from '@heroicons/react/24/outline'
import { Outlet, useLocation } from 'react-router-dom'

import { Button } from '@/components/ui/Button'
import { MobileNav } from '@/components/layout/MobileNav'
import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'

function describePath(pathname: string) {
  const labels: Record<string, { title: string; subtitle: string }> = {
    '/student': { title: 'Student dashboard', subtitle: 'Track your academic standing, grades, and registrations.' },
    '/student/courses': { title: 'My courses', subtitle: 'Review your active sections and academic schedule.' },
    '/student/grades': { title: 'My grades', subtitle: 'Review official grade records and transcript actions.' },
    '/student/register': { title: 'Course registration', subtitle: 'Register, review, and drop sections in one place.' },
    '/student/corrections': { title: 'Correction requests', subtitle: 'Submit and track record correction requests.' },
    '/advisor': { title: 'Advisor dashboard', subtitle: 'Prioritise advisees, notes, and intervention signals.' },
    '/advisor/alerts': { title: 'Alert history', subtitle: 'Track acknowledged and deferred advisory concerns.' },
    '/faculty': { title: 'Faculty dashboard', subtitle: 'Manage assigned sections, rosters, grades, and attendance.' },
    '/admin': { title: 'Admin dashboard', subtitle: 'Oversee users, records, and institutional operations.' },
    '/admin/users': { title: 'User administration', subtitle: 'Create, edit, deactivate, and reset user accounts.' },
    '/admin/courses': { title: 'Courses', subtitle: 'Manage academic records, sections, and catalog visibility.' },
    '/admin/audit-log': { title: 'AI audit log', subtitle: 'Review governance and operational records when available.' },
    '/account/password': { title: 'Password settings', subtitle: 'Update your password and session posture.' },
  }

  return labels[pathname] ?? { title: 'Student Information System', subtitle: 'Role-specific academic operations.' }
}

export function AppShell() {
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const heading = useMemo(() => describePath(location.pathname), [location.pathname])

  return (
    <div className="min-h-screen bg-transparent text-neutral-900">
      <MobileNav open={mobileOpen} onOpenChange={setMobileOpen} />
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="min-w-0 flex-1">
          <div className="flex h-16 items-center justify-between border-b border-neutral-200 bg-primary px-4 text-white lg:hidden">
            <p className="font-display text-lg font-bold">Student Information System</p>
            <Button variant="ghost" size="sm" className="min-w-0 px-2 text-white hover:bg-white/10" onClick={() => setMobileOpen(true)}>
              <Bars3Icon className="h-5 w-5" />
            </Button>
          </div>
          <Topbar title={heading.title} subtitle={heading.subtitle} />
          <main className="mx-auto max-w-page px-4 py-6 sm:px-6 lg:px-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
