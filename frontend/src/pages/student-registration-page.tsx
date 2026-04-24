import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useDeferredValue, useMemo, useState } from 'react'

import { createEnrollment, dropEnrollment, getEnrollments, getSections } from '@/api/academics'
import { useAuth } from '@/auth/auth-context'
import { DataState } from '@/components/ui/data-state'
import { MetricStrip } from '@/components/ui/metric-strip'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'
import { formatDateTime, isOpenWindow } from '@/utils/format'

export function StudentRegistrationPage() {
  const queryClient = useQueryClient()
  const { session } = useAuth()
  const [searchTerm, setSearchTerm] = useState('')
  const deferredSearchTerm = useDeferredValue(searchTerm)
  const [feedbackMessage, setFeedbackMessage] = useState('')

  const sectionsQuery = useQuery({
    queryKey: ['sections', 'student-registration'],
    queryFn: getSections,
  })
  const enrollmentsQuery = useQuery({
    queryKey: ['enrollments', 'student-registration'],
    queryFn: () => getEnrollments(),
  })

  const enrollMutation = useMutation({
    mutationFn: createEnrollment,
    onSuccess: async () => {
      setFeedbackMessage('Enrollment submitted.')
      await queryClient.invalidateQueries({ queryKey: ['enrollments', 'student-registration'] })
    },
  })
  const dropMutation = useMutation({
    mutationFn: ({ enrollmentId }: { enrollmentId: string }) => dropEnrollment(enrollmentId),
    onSuccess: async () => {
      setFeedbackMessage('Enrollment dropped.')
      await queryClient.invalidateQueries({ queryKey: ['enrollments', 'student-registration'] })
    },
  })

  const enrollmentBySectionId = useMemo(() => {
    return new Map((enrollmentsQuery.data ?? []).map((enrollment) => [enrollment.section_id, enrollment]))
  }, [enrollmentsQuery.data])

  const visibleSections = useMemo(() => {
    const normalizedTerm = deferredSearchTerm.trim().toLowerCase()
    return (sectionsQuery.data ?? []).filter((section) => {
      if (!normalizedTerm) {
        return true
      }
      return `${section.course_code} ${section.course_title} ${section.section_code}`
        .toLowerCase()
        .includes(normalizedTerm)
    })
  }, [deferredSearchTerm, sectionsQuery.data])

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Student registration"
        title="Enroll and drop within the active window"
        description="Course sections are filtered to the student's programme. Enrollments and drops call the live REST endpoints from the verified Step 2.3 backend."
      />

      <MetricStrip
        items={[
          {
            label: 'Active sections',
            value: String(visibleSections.length),
          },
          {
            label: 'Current enrollments',
            value: String(enrollmentsQuery.data?.length ?? 0),
          },
          {
            label: 'Signed in as',
            value: session?.user.username ?? 'Unknown',
            accent: 'text-teal-700',
          },
        ]}
      />

      <Panel
        title="Available sections"
        description="The list below supports self-enrollment during the registration window and drop actions for current enrollments."
        action={
          <input
            aria-label="Search sections"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Filter by course or section"
            className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 text-sm outline-none transition focus:border-slate-900"
          />
        }
      >
        {feedbackMessage ? (
          <div className="mb-4 rounded-2xl border border-teal-200 bg-teal-50 px-4 py-3 text-sm text-teal-800">
            {feedbackMessage}
          </div>
        ) : null}

        {sectionsQuery.isLoading || enrollmentsQuery.isLoading ? (
          <DataState title="Loading registration data" message="Fetching sections and current enrollments." />
        ) : null}

        {sectionsQuery.isError ? (
          <DataState
            title="Section load failed"
            message="The section catalog could not be loaded from the backend."
          />
        ) : null}

        {!sectionsQuery.isLoading && !sectionsQuery.isError ? (
          <div className="grid gap-4">
            {visibleSections.map((section) => {
              const enrollment = enrollmentBySectionId.get(section.id)
              const canEnroll = isOpenWindow(section.registration_opens_at, section.registration_closes_at) && !enrollment

              return (
                <article
                  key={section.id}
                  className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{section.course_code}</p>
                      <h3 className="mt-2 text-xl font-semibold text-slate-900">{section.course_title}</h3>
                      <p className="mt-1 text-sm text-slate-600">
                        Section {section.section_code} · {section.room} · {section.faculty_full_name}
                      </p>
                    </div>
                    <div className="text-right text-xs text-slate-500">
                      <p>{section.current_enrollment_count} / {section.max_capacity} seats</p>
                      <p className="mt-1">Opens {formatDateTime(section.registration_opens_at)}</p>
                    </div>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-3">
                    {enrollment ? (
                      <button
                        type="button"
                        onClick={() => {
                          setFeedbackMessage('')
                          dropMutation.mutate({ enrollmentId: enrollment.id })
                        }}
                        disabled={dropMutation.isPending}
                        className="min-h-11 rounded-2xl border border-red-300 bg-red-50 px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-70"
                      >
                        {dropMutation.isPending ? 'Dropping...' : 'Drop'}
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={() => {
                          setFeedbackMessage('')
                          enrollMutation.mutate({
                            sectionId: section.id,
                            waitlistIfFull: false,
                          })
                        }}
                        disabled={!canEnroll || enrollMutation.isPending}
                        className="min-h-11 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
                      >
                        {enrollMutation.isPending ? 'Submitting...' : 'Enroll'}
                      </button>
                    )}

                    <div className="min-h-11 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
                      {enrollment
                        ? `Current status: ${enrollment.enrollment_status}`
                        : canEnroll
                          ? 'Registration window is open'
                          : 'Registration window is closed'}
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        ) : null}
      </Panel>
    </div>
  )
}

export default StudentRegistrationPage
