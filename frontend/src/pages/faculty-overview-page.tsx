import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { getSections } from '@/api/academics'
import { DataState } from '@/components/ui/data-state'
import { MetricStrip } from '@/components/ui/metric-strip'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'
import { RoadmapPanel } from '@/components/ui/roadmap-panel'

export default function FacultyOverviewPage() {
  const sectionsQuery = useQuery({
    queryKey: ['sections', 'faculty-overview'],
    queryFn: getSections,
  })

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Faculty dashboard"
        title="Sections, rosters, and grade entry"
        description="Faculty access is limited to assigned sections. This dashboard provides roster and grade-entry entry points."
      />

      <MetricStrip
        items={[
          {
            label: 'Assigned sections',
            value: String(sectionsQuery.data?.length ?? 0),
          },
        ]}
      />

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel title="Assigned sections" description="Open a section to view the roster and enter draft grades.">
          {sectionsQuery.isLoading ? (
            <DataState title="Loading sections" message="Fetching faculty-assigned sections." />
          ) : sectionsQuery.isError ? (
            <DataState title="Section load failed" message="Assigned sections could not be loaded." />
          ) : sectionsQuery.data && sectionsQuery.data.length ? (
            <div className="grid gap-3">
              {sectionsQuery.data.map((section) => (
                <Link
                  key={section.id}
                  to={`/faculty/sections/${section.id}`}
                  className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] px-4 py-4 transition hover:border-slate-900"
                >
                  <p className="text-lg font-semibold text-slate-900">
                    {section.course_code} · Section {section.section_code}
                  </p>
                  <p className="mt-1 text-sm text-slate-600">{section.course_title}</p>
                  <p className="mt-1 text-sm text-slate-600">{section.current_enrollment_count} enrolled</p>
                </Link>
              ))}
            </div>
          ) : (
            <DataState title="No sections" message="No assigned sections are available for this faculty account." />
          )}
        </Panel>

        <RoadmapPanel
          title="Moodle engagement view"
          requirement="FR-STU-006"
          description="Faculty-side Moodle engagement appears in the later Moodle integration phase."
        />
      </div>
    </div>
  )
}
