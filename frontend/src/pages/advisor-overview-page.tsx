import { useQuery } from '@tanstack/react-query'
import { useDeferredValue, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { getStudents } from '@/api/students'
import { DataState } from '@/components/ui/data-state'
import { MetricStrip } from '@/components/ui/metric-strip'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'
import { RoadmapPanel } from '@/components/ui/roadmap-panel'

export default function AdvisorOverviewPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const deferredSearchTerm = useDeferredValue(searchTerm)
  const studentsQuery = useQuery({
    queryKey: ['students', 'advisor-overview'],
    queryFn: getStudents,
  })

  const visibleStudents = useMemo(() => {
    const normalizedTerm = deferredSearchTerm.trim().toLowerCase()
    return (studentsQuery.data ?? []).filter((student) => {
      if (!normalizedTerm) {
        return true
      }
      return `${student.full_name} ${student.student_number} ${student.programme}`
        .toLowerCase()
        .includes(normalizedTerm)
    })
  }, [deferredSearchTerm, studentsQuery.data])

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Advisor dashboard"
        title="Assigned students and unified profiles"
        description="Advisor access is scoped to assigned students. This area supports student search, unified profiles, notes, financial visibility, and grade history."
      />

      <MetricStrip
        items={[
          {
            label: 'Assigned students',
            value: String(studentsQuery.data?.length ?? 0),
          },
          {
            label: 'Probation cases',
            value: String(
              (studentsQuery.data ?? []).filter((student) => student.academic_standing !== 'GOOD').length,
            ),
            accent: 'text-orange-600',
          },
        ]}
      />

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel
          title="Student search"
          description="Build the unified student profile from the assigned-student list early, as directed by the setup guide."
          action={
            <input
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search by name, student number, or programme"
              className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 text-sm outline-none transition focus:border-slate-900"
            />
          }
        >
          {studentsQuery.isLoading ? (
            <DataState title="Loading students" message="Fetching advisor-assigned students." />
          ) : studentsQuery.isError ? (
            <DataState title="Student load failed" message="The assigned student list could not be loaded." />
          ) : visibleStudents.length ? (
            <div className="grid gap-3">
              {visibleStudents.map((student) => (
                <Link
                  key={student.id}
                  to={`/advisor/students/${student.id}`}
                  className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] px-4 py-4 transition hover:border-slate-900"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-lg font-semibold text-slate-900">{student.full_name}</p>
                      <p className="mt-1 text-sm text-slate-600">{student.student_number}</p>
                      <p className="mt-1 text-sm text-slate-600">{student.programme}</p>
                    </div>
                    <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                      {student.academic_standing}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <DataState title="No matching students" message="Try a broader search term." />
          )}
        </Panel>

        <RoadmapPanel
          title="At-risk alerts"
          requirement="AI-RSK-001"
          description="Alert generation lands in the later AI phase once the nightly engine and audit log surface exist."
        />
      </div>
    </div>
  )
}
