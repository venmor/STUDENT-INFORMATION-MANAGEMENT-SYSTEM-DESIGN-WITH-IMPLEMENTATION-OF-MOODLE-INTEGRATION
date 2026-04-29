import { useEffect, useState } from 'react'

import { AcademicCapIcon, IdentificationIcon, UserGroupIcon } from '@heroicons/react/24/outline'

import { fetchLtiSessionContext } from '@/api/lti'
import { Alert } from '@/components/ui/Alert'
import { Badge } from '@/components/ui/Badge'
import { Card, CardTitle } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import type { LtiSessionContext } from '@/types/lti'

export function AdvisingToolPage() {
  const [context, setContext] = useState<LtiSessionContext | null>(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let isMounted = true

    fetchLtiSessionContext('advising-dashboard')
      .then((payload) => {
        if (isMounted) {
          setContext(payload)
        }
      })
      .catch((loadError: unknown) => {
        if (isMounted) {
          setError(loadError instanceof Error ? loadError.message : 'Unable to load this LTI tool.')
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false)
        }
      })

    return () => {
      isMounted = false
    }
  }, [])

  if (isLoading) {
    return (
      <main className="min-h-screen bg-neutral-50 px-4 py-8">
        <div className="mx-auto flex max-w-5xl items-center gap-3 text-sm text-neutral-700">
          <Spinner size="sm" />
          Loading verified LTI context
        </div>
      </main>
    )
  }

  if (error || !context) {
    return (
      <main className="min-h-screen bg-neutral-50 px-4 py-8">
        <div className="mx-auto max-w-5xl">
          <Alert tone="danger" title="LTI launch required">
            {error || 'Open this tool from Moodle so the SIS can validate the launch.'}
          </Alert>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-neutral-50 px-4 py-8 text-neutral-900">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="flex flex-col gap-4 border-b border-neutral-200 pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-info">Moodle LTI verified</p>
            <h1 className="mt-1 text-2xl font-semibold">Advising dashboard</h1>
            <p className="mt-2 max-w-2xl text-sm text-neutral-600">
              Read-only SIS advising context launched from Moodle.
            </p>
          </div>
          <Badge tone={context.isMapped ? 'success' : 'warning'}>{context.isMapped ? 'Mapped SIS context' : 'Unmapped launch'}</Badge>
        </header>

        {!context.isMapped ? (
          <Alert tone="warning" title="Limited launch context">
            Moodle launch validation succeeded, but the Moodle user or course is not mapped to SIS records yet. Run Lane A
            provisioning and confirm `MoodleUserMap` and `MoodleCourseMap` before using roster data.
          </Alert>
        ) : null}

        <section className="grid gap-4 md:grid-cols-3">
          <Card className="md:col-span-2">
            <div className="mb-4 flex items-center gap-2">
              <AcademicCapIcon className="h-5 w-5 text-info" />
              <CardTitle>Course context</CardTitle>
            </div>
            {context.section ? (
              <dl className="grid gap-3 text-sm sm:grid-cols-2">
                <Info label="Course" value={`${context.section.courseCode} ${context.section.courseTitle}`} />
                <Info label="Section" value={context.section.sectionCode} />
                <Info label="Term" value={`${context.section.semester} ${context.section.academicYear}`} />
                <Info label="Faculty" value={context.section.faculty} />
              </dl>
            ) : (
              <p className="text-sm text-neutral-600">{context.launch.context.title ?? 'No mapped SIS section available.'}</p>
            )}
          </Card>

          <Card>
            <div className="mb-4 flex items-center gap-2">
              <IdentificationIcon className="h-5 w-5 text-info" />
              <CardTitle>Launch identity</CardTitle>
            </div>
            <dl className="space-y-3 text-sm">
              <Info label="Moodle user" value={context.launch.moodleUserId || context.launch.moodleSubject} />
              <Info label="SIS user" value={context.sisUser?.username ?? 'Not mapped'} />
              <Info label="SIS role" value={context.sisUser?.primaryRole ?? 'Limited'} />
            </dl>
          </Card>
        </section>

        <Card>
          <div className="mb-4 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <UserGroupIcon className="h-5 w-5 text-info" />
              <CardTitle>Course roster</CardTitle>
            </div>
            <Badge>{context.roster.length} students</Badge>
          </div>
          {context.roster.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-neutral-200 text-sm">
                <thead>
                  <tr className="text-left text-xs font-semibold uppercase tracking-wide text-neutral-500">
                    <th className="px-3 py-2">Student</th>
                    <th className="px-3 py-2">Student number</th>
                    <th className="px-3 py-2">Email</th>
                    <th className="px-3 py-2">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-100">
                  {context.roster.map((student) => (
                    <tr key={student.studentId}>
                      <td className="px-3 py-3 font-medium text-neutral-900">{student.fullName}</td>
                      <td className="px-3 py-3 text-neutral-700">{student.studentNumber}</td>
                      <td className="px-3 py-3 text-neutral-700">{student.email}</td>
                      <td className="px-3 py-3">
                        <Badge tone="info">{student.enrollmentStatus}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-neutral-600">No SIS roster is available for this launch context.</p>
          )}
        </Card>
      </div>
    </main>
  )
}

function Info({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">{label}</dt>
      <dd className="mt-1 break-words text-neutral-900">{value}</dd>
    </div>
  )
}
