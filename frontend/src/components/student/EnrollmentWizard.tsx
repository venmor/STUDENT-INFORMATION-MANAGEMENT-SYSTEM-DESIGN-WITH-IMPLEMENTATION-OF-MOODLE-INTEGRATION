import { useMemo, useState } from 'react'

import { RectangleStackIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Select } from '@/components/ui/Select'
import type { CourseSection, Enrollment } from '@/types'

export function EnrollmentWizard({
  enrollments,
  isSubmitting,
  onDrop,
  onEnroll,
  sections,
}: {
  enrollments: Enrollment[]
  isSubmitting: boolean
  onDrop: (enrollmentId: string) => void
  onEnroll: (sectionId: string) => void
  sections: CourseSection[]
}) {
  const [sectionId, setSectionId] = useState('')
  const availableOptions = useMemo(
    () =>
      sections.map((section) => ({
        label: `${section.course_code} · ${section.section_code} · ${section.faculty_full_name}`,
        value: section.id,
      })),
    [sections],
  )

  return (
    <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <Card>
        <CardTitle>Available sections</CardTitle>
        <div className="mt-4">
          {availableOptions.length ? (
            <div className="space-y-4">
              <Select
                id="section-select"
                label="Select a section"
                items={availableOptions}
                placeholder="Choose a section"
                value={sectionId}
                onValueChange={setSectionId}
              />
              <Button loading={isSubmitting} onClick={() => sectionId && onEnroll(sectionId)}>
                Register for selected section
              </Button>
            </div>
          ) : (
            <EmptyState
              icon={<RectangleStackIcon className="h-12 w-12" />}
              title="No sections available"
              description="There are no open sections available for registration in the current dataset."
            />
          )}
        </div>
      </Card>
      <Card>
        <CardTitle>Current registrations</CardTitle>
        <div className="mt-4">
          {enrollments.length ? (
            <div className="space-y-3">
              {enrollments.map((enrollment) => (
                <div
                  key={enrollment.id}
                  className="flex items-center justify-between rounded-xl border border-neutral-200 px-4 py-3"
                >
                  <div>
                    <p className="font-mono text-xs text-neutral-500">{enrollment.section.course_code}</p>
                    <p className="font-medium text-neutral-900">{enrollment.section.course_title}</p>
                  </div>
                  <Button variant="secondary" size="sm" onClick={() => onDrop(enrollment.id)}>
                    Drop
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={<RectangleStackIcon className="h-12 w-12" />}
              title="No registrations yet"
              description="Your current registration list is empty. Choose a section on the left to begin."
            />
          )}
        </div>
      </Card>
    </div>
  )
}
