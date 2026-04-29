import { useEffect, useState } from 'react'

import { ClipboardDocumentListIcon, IdentificationIcon } from '@heroicons/react/24/outline'

import { fetchLtiSessionContext } from '@/api/lti'
import { Alert } from '@/components/ui/Alert'
import { Badge } from '@/components/ui/Badge'
import { Card, CardTitle } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import type { LtiSessionContext } from '@/types/lti'

export function RegistrationToolPage() {
  const [context, setContext] = useState<LtiSessionContext | null>(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let isMounted = true

    fetchLtiSessionContext('registration')
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
      <div className="mx-auto max-w-5xl space-y-6">
        <header className="flex flex-col gap-4 border-b border-neutral-200 pb-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-info">Moodle LTI verified</p>
            <h1 className="mt-1 text-2xl font-semibold">Registration</h1>
            <p className="mt-2 max-w-2xl text-sm text-neutral-600">
              Read-only registration context launched from Moodle.
            </p>
          </div>
          <Badge tone={context.isMapped ? 'success' : 'warning'}>{context.isMapped ? 'Mapped SIS student' : 'Unmapped launch'}</Badge>
        </header>

        <Alert tone="info" title="Registration actions remain governed by SIS rules">
          This embedded Step 3.3 tool shows verified launch and enrollment context. Register and drop actions stay in the
          standard SIS enrollment workflow until Step 3.4 verifies the full Moodle launch-to-SIS action path.
        </Alert>

        {!context.isMapped ? (
          <Alert tone="warning" title="Limited launch context">
            Moodle launch validation succeeded, but the Moodle user is not mapped to an active SIS student record yet.
          </Alert>
        ) : null}

        <section className="grid gap-4 md:grid-cols-2">
          <Card>
            <div className="mb-4 flex items-center gap-2">
              <IdentificationIcon className="h-5 w-5 text-info" />
              <CardTitle>Student context</CardTitle>
            </div>
            {context.student ? (
              <dl className="grid gap-3 text-sm">
                <Info label="Student" value={context.student.fullName} />
                <Info label="Student number" value={context.student.studentNumber} />
                <Info label="Programme" value={context.student.programme} />
                <Info label="Standing" value={context.student.academicStanding} />
              </dl>
            ) : (
              <p className="text-sm text-neutral-600">No mapped SIS student is available for this launch.</p>
            )}
          </Card>

          <Card>
            <div className="mb-4 flex items-center gap-2">
              <ClipboardDocumentListIcon className="h-5 w-5 text-info" />
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
            <CardTitle>Current enrollments</CardTitle>
            <Badge>{context.enrollments.length} active</Badge>
          </div>
          {context.enrollments.length > 0 ? (
            <div className="grid gap-3">
              {context.enrollments.map((enrollment) => (
                <div
                  key={enrollment.enrollmentId}
                  className="rounded-md border border-neutral-200 bg-neutral-50 px-4 py-3 text-sm"
                >
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <p className="font-medium text-neutral-900">
                        {enrollment.courseCode} {enrollment.courseTitle}
                      </p>
                      <p className="mt-1 text-neutral-600">
                        Section {enrollment.sectionCode}, {enrollment.semester} {enrollment.academicYear}
                      </p>
                    </div>
                    <Badge tone="info">{enrollment.enrollmentStatus}</Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-neutral-600">No active SIS enrollments are available for this launch context.</p>
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
