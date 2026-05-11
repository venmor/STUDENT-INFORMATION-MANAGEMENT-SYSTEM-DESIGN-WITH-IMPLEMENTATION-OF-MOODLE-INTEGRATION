import { Link } from 'react-router-dom'
import { ArrowTopRightOnSquareIcon, BookOpenIcon, ChartBarIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline'

import { DeferredFeaturePanel } from '@/components/ui/DeferredFeaturePanel'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { CourseCard } from '@/components/student/CourseCard'
import { QuickStatsPanel } from '@/components/student/QuickStatsPanel'
import { Card, CardTitle } from '@/components/ui/Card'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import { useEnrollments } from '@/hooks/useEnrollments'
import { useStudent } from '@/hooks/useStudents'

export function StudentDashboardPage() {
  const user = useCurrentUser()
  const student = useStudent(user?.studentProfileId ?? undefined)
  const enrollments = useEnrollments({ studentId: user?.studentProfileId ?? undefined })

  if (student.isPending) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-36" />
          <Skeleton className="h-36" />
          <Skeleton className="h-36" />
        </div>
        <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <Skeleton className="h-80" />
          <Skeleton className="h-80" />
        </div>
      </div>
    )
  }

  if (!student.data) {
    return (
      <EmptyState
        icon={<ChartBarIcon className="h-12 w-12" />}
        title="Student record unavailable"
        description="The dashboard could not load your student profile. Refresh the page or contact the registrar if the problem continues."
      />
    )
  }

  return (
    <div className="space-y-6">
      <section className="space-y-4">
        <div>
          <p className="text-sm text-neutral-500">Good day</p>
          <h2 className="font-display text-3xl font-bold text-neutral-900">{student.data.full_name}</h2>
        </div>
        <QuickStatsPanel student={student.data} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardTitle>This semester&apos;s courses</CardTitle>
          <div className="mt-4">
            {enrollments.data?.length ? (
              <div className="grid gap-4 md:grid-cols-2">
                {enrollments.data.slice(0, 4).map((enrollment) => (
                  <CourseCard key={enrollment.id} enrollment={enrollment} />
                ))}
              </div>
            ) : (
              <EmptyState
                icon={<BookOpenIcon className="h-12 w-12" />}
                title="No active course registrations"
                description="Use the registration workspace to add a section, then your semester load will appear here."
              />
            )}
          </div>
        </Card>
        <div className="space-y-6">
          <Card>
            <CardTitle>Recent activity</CardTitle>
            <div className="mt-4 space-y-4 text-sm text-neutral-600">
              <div className="flex items-center justify-between">
                <span>Student profile active</span>
                <span>{student.data.programme}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Attendance summaries available</span>
                <span className="font-mono">{student.data.attendance_percentages.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Transcript access</span>
                <span className="inline-flex items-center gap-1 text-secondary">
                  Enabled
                  <ArrowTopRightOnSquareIcon className="h-4 w-4" />
                </span>
              </div>
            </div>
          </Card>
          <Card>
            <div className="flex items-start gap-3">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-primary-light text-primary">
                <ChatBubbleLeftRightIcon className="h-6 w-6" aria-hidden="true" />
              </div>
              <div>
                <CardTitle>AI Co-pilot</CardTitle>
                <p className="mt-2 text-sm leading-6 text-neutral-600">
                  Ask source-grounded questions about registration, deadlines, documents, courses, and grades.
                </p>
                <Link
                  to="/student/copilot"
                  className="mt-3 inline-flex min-h-11 items-center rounded-lg border border-primary/20 px-3 text-sm font-semibold text-primary hover:bg-primary-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                >
                  Open AI Co-pilot
                </Link>
              </div>
            </div>
          </Card>
          <DeferredFeaturePanel phaseLabel="Phase 4" title="Wellbeing check-in">
            The student wellbeing workflow remains a later-phase feature. The UI is reserved here so the
            portal structure matches the approved SRS without pretending the safeguarded backend exists yet.
          </DeferredFeaturePanel>
        </div>
      </section>
    </div>
  )
}
