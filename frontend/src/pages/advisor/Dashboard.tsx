import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { useDeferredValue, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { AtRiskAlertQueue } from '@/components/advisor/AtRiskAlertQueue'
import { StudentSearchBar } from '@/components/advisor/StudentSearchBar'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { useStudents } from '@/hooks/useStudents'

export function AdvisorDashboardPage() {
  const { data: students = [] } = useStudents()
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)
  const filtered = useMemo(() => {
    const normalized = deferredQuery.trim().toLowerCase()
    if (!normalized) {
      return students.slice(0, 6)
    }
    return students.filter(
      (student) =>
        student.full_name.toLowerCase().includes(normalized) ||
        student.student_number.toLowerCase().includes(normalized),
    )
  }, [deferredQuery, students])

  return (
    <div className="space-y-6">
      <Card>
        <CardTitle>Student search</CardTitle>
        <div className="mt-4">
          <StudentSearchBar value={query} onChange={setQuery} />
        </div>
        <div className="mt-4">
          {filtered.length ? (
            <div className="grid gap-3 md:grid-cols-2">
              {filtered.map((student) => (
                <Link
                  key={student.id}
                  to={`/advisor/students/${student.id}`}
                  className="rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-3 hover:border-primary"
                >
                  <p className="font-medium text-neutral-900">{student.full_name}</p>
                  <p className="mt-1 font-mono text-xs text-neutral-500">{student.student_number}</p>
                </Link>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={<MagnifyingGlassIcon className="h-12 w-12" />}
              title="No advisees matched your search"
              description="Search by student name or student number to open a unified student profile."
            />
          )}
        </div>
      </Card>
      <Card>
        <Link to="/advisor/alerts" className="hover:text-primary">
          <CardTitle>At-risk alerts &rarr;</CardTitle>
        </Link>
        <div className="mt-4">
          <AtRiskAlertQueue />
        </div>
      </Card>
    </div>
  )
}
