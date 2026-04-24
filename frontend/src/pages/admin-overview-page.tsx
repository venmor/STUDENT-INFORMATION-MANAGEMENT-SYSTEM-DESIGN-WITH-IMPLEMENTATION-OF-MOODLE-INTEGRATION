import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { getSections } from '@/api/academics'
import { getAdvisorProbe } from '@/api/auth'
import { getStudents } from '@/api/students'
import { getUsers } from '@/api/users'
import { DataState } from '@/components/ui/data-state'
import { MetricStrip } from '@/components/ui/metric-strip'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'

export default function AdminOverviewPage() {
  const usersQuery = useQuery({
    queryKey: ['users', 'admin-overview'],
    queryFn: getUsers,
  })
  const studentsQuery = useQuery({
    queryKey: ['students', 'admin-overview'],
    queryFn: getStudents,
  })
  const sectionsQuery = useQuery({
    queryKey: ['sections', 'admin-overview'],
    queryFn: getSections,
  })
  const advisorProbeQuery = useQuery({
    queryKey: ['auth-probe', 'advisor', 'admin-overview'],
    queryFn: getAdvisorProbe,
  })

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Admin dashboard"
        title="Operational control panel"
        description="This area aggregates user administration, student-record operations, and a Phase 2 system snapshot from the live API."
      />

      <MetricStrip
        items={[
          { label: 'Users', value: String(usersQuery.data?.length ?? 0) },
          { label: 'Students', value: String(studentsQuery.data?.length ?? 0) },
          { label: 'Active sections', value: String(sectionsQuery.data?.length ?? 0) },
          {
            label: 'Route policy status',
            value: advisorProbeQuery.isSuccess ? 'Healthy' : 'Checking',
            accent: advisorProbeQuery.isSuccess ? 'text-teal-700' : 'text-orange-600',
          },
        ]}
      />

      <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <Panel title="Student operations" description="Admins can open any student record for flags, corrections, advising-note approval, and grade officialisation.">
          {studentsQuery.isLoading ? (
            <DataState title="Loading students" message="Fetching student records." />
          ) : studentsQuery.isError ? (
            <DataState title="Student load failed" message="Student records could not be loaded." />
          ) : studentsQuery.data && studentsQuery.data.length ? (
            <div className="grid gap-3">
              {studentsQuery.data.slice(0, 8).map((student) => (
                <Link
                  key={student.id}
                  to={`/admin/students/${student.id}`}
                  className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] px-4 py-4 transition hover:border-slate-900"
                >
                  <p className="text-lg font-semibold text-slate-900">{student.full_name}</p>
                  <p className="mt-1 text-sm text-slate-600">{student.student_number}</p>
                </Link>
              ))}
            </div>
          ) : (
            <DataState title="No students" message="No student records are available yet." />
          )}
        </Panel>

        <Panel title="System snapshot" description="Built from currently available Phase 2 endpoints instead of placeholder health claims.">
          <div className="grid gap-3">
            <div className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
              <p className="text-sm font-semibold text-slate-900">Advisor probe</p>
              <p className="mt-2 text-sm text-slate-600">
                {advisorProbeQuery.isSuccess
                  ? advisorProbeQuery.data.detail
                  : 'Checking RBAC probe availability through the live API.'}
              </p>
            </div>
            <Link
              to="/admin/users"
              className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] px-4 py-4 text-sm font-semibold text-slate-900 transition hover:border-slate-900"
            >
              Open user administration
            </Link>
          </div>
        </Panel>
      </div>
    </div>
  )
}
