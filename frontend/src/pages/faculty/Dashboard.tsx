import { AcademicCapIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import { useSections } from '@/hooks/useCourses'

export function FacultyDashboardPage() {
  const user = useCurrentUser()
  const sections = useSections()
  const assigned = (sections.data ?? []).filter((section) => section.faculty_user_id === user?.id)

  return (
    <Card>
      <CardTitle>Assigned sections</CardTitle>
      <div className="mt-4">
        {assigned.length ? (
          <div className="grid gap-4 lg:grid-cols-2">
            {assigned.map((section) => (
              <Link
                key={section.id}
                to={`/faculty/sections/${section.id}`}
                className="rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-4 hover:border-primary"
              >
                <p className="font-mono text-xs text-neutral-500">{section.course_code}</p>
                <p className="mt-1 font-semibold text-neutral-900">{section.course_title}</p>
                <p className="mt-2 text-sm text-neutral-500">
                  Section {section.section_code} · {section.semester}
                </p>
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<AcademicCapIcon className="h-12 w-12" />}
            title="No assigned sections"
            description="Faculty section workspaces appear here after academic scheduling assigns you to a section."
          />
        )}
      </div>
    </Card>
  )
}
