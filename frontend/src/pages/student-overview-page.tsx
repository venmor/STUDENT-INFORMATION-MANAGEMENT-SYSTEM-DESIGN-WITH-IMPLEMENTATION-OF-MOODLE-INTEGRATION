import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { getEnrollments, getGrades } from '@/api/academics'
import { getStudent } from '@/api/students'
import { useAuth } from '@/auth/auth-context'
import { DataState } from '@/components/ui/data-state'
import { MetricStrip } from '@/components/ui/metric-strip'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'
import { RoadmapPanel } from '@/components/ui/roadmap-panel'

export default function StudentOverviewPage() {
  const { session } = useAuth()
  const studentId = session?.user.studentProfileId

  const studentQuery = useQuery({
    queryKey: ['student', studentId],
    queryFn: () => getStudent(studentId as string),
    enabled: Boolean(studentId),
  })
  const gradesQuery = useQuery({
    queryKey: ['grades', 'student-self'],
    queryFn: () => getGrades(),
  })
  const enrollmentsQuery = useQuery({
    queryKey: ['enrollments', 'student-self'],
    queryFn: () => getEnrollments(),
  })

  if (!studentId) {
    return (
      <DataState
        title="Student profile not linked"
        message="This account has no student profile identifier in the session payload yet."
      />
    )
  }

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Student dashboard"
        title="Academic record at a glance"
        description="Profile, official grades, registration, transcript access, and correction requests live in the student area."
        actions={
          <Link
            to="/student/registration"
            className="inline-flex min-h-11 items-center rounded-2xl border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/16"
          >
            Open registration
          </Link>
        }
      />

      <MetricStrip
        items={[
          {
            label: 'Cumulative GPA',
            value: studentQuery.data?.cumulative_gpa ?? '0.00',
            accent: 'text-teal-700',
          },
          {
            label: 'Academic standing',
            value: studentQuery.data?.academic_standing ?? 'Unknown',
          },
          {
            label: 'Official grades',
            value: String(gradesQuery.data?.length ?? 0),
          },
          {
            label: 'Active enrollments',
            value: String(enrollmentsQuery.data?.length ?? 0),
          },
        ]}
      />

      <div className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <Panel
          title="Profile snapshot"
          description="The student profile endpoint supplies the unified record, including attendance percentages and attendance flags."
        >
          {studentQuery.isLoading ? (
            <DataState title="Loading student profile" message="Fetching the current student record." />
          ) : studentQuery.isError || !studentQuery.data ? (
            <DataState title="Profile load failed" message="The student profile could not be loaded from the backend." />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Identity</p>
                <p className="mt-3 text-lg font-semibold text-slate-900">{studentQuery.data.full_name}</p>
                <p className="mt-1 text-sm text-slate-600">{studentQuery.data.student_number}</p>
                <p className="mt-1 text-sm text-slate-600">{studentQuery.data.programme}</p>
              </div>
              <div className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Attendance flags</p>
                {studentQuery.data.attendance_flags.length ? (
                  <ul className="mt-3 space-y-2 text-sm text-slate-700">
                    {studentQuery.data.attendance_flags.map((flag) => (
                      <li key={flag.section_id}>
                        {flag.course_code}: {flag.attendance_percentage}% below threshold {flag.threshold}%
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-3 text-sm text-slate-600">No low-attendance flags are active.</p>
                )}
              </div>
              <div className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4 md:col-span-2">
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Attendance percentages</p>
                {studentQuery.data.attendance_percentages.length ? (
                  <div className="mt-3 overflow-x-auto">
                    <table className="min-w-full text-left text-sm text-slate-700">
                      <thead className="text-xs uppercase tracking-[0.2em] text-slate-500">
                        <tr>
                          <th className="pb-2">Course</th>
                          <th className="pb-2">Attendance</th>
                          <th className="pb-2">Threshold</th>
                        </tr>
                      </thead>
                      <tbody>
                        {studentQuery.data.attendance_percentages.map((row) => (
                          <tr key={row.section_id} className="border-t border-slate-200">
                            <td className="py-3">{row.course_code}</td>
                            <td className="py-3">{row.attendance_percentage}%</td>
                            <td className="py-3">{row.threshold}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="mt-3 text-sm text-slate-600">Attendance sessions have not been recorded yet.</p>
                )}
              </div>
            </div>
          )}
        </Panel>

        <div className="space-y-5">
          <Panel title="Next actions" description="Jump straight into the most common student tasks.">
            <div className="grid gap-3">
              <Link
                to="/student/grades"
                className="rounded-2xl border border-slate-200 bg-[#fffdfa] px-4 py-4 text-sm font-semibold text-slate-900 transition hover:border-slate-900"
              >
                View official grades and transcript
              </Link>
              <Link
                to="/student/corrections"
                className="rounded-2xl border border-slate-200 bg-[#fffdfa] px-4 py-4 text-sm font-semibold text-slate-900 transition hover:border-slate-900"
              >
                Submit record correction requests
              </Link>
            </div>
          </Panel>

          <RoadmapPanel
            title="Student service co-pilot"
            requirement="AI-COP-001"
            description="The chat surface is reserved here, but the governed LLM backend arrives in later phases."
          />
        </div>
      </div>
    </div>
  )
}
