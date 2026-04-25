import { ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline'

import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import type { Enrollment } from '@/types'
import { formatPercentage } from '@/utils/formatters'

export function CourseCard({ enrollment }: { enrollment: Enrollment }) {
  const section = enrollment.section

  return (
    <Card interactive className="space-y-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-mono text-sm uppercase tracking-wide text-neutral-500">{section.course_code}</p>
          <h3 className="mt-1 text-base font-semibold text-neutral-900">{section.course_title}</h3>
        </div>
        <Badge tone={enrollment.is_active ? 'success' : 'warning'}>
          {enrollment.is_active ? 'Active' : enrollment.enrollment_status}
        </Badge>
      </div>
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm text-neutral-500">
          <span>Section {section.section_code}</span>
          <span>{section.semester}</span>
        </div>
        <div>
          <div className="flex items-center justify-between text-sm text-neutral-700">
            <span>Attendance</span>
            <span>{formatPercentage(section.attendance_threshold)}</span>
          </div>
          <div className="mt-2 h-1.5 rounded-full bg-neutral-200">
            <div className="h-1.5 w-3/4 rounded-full bg-primary" />
          </div>
        </div>
      </div>
      <div className="flex items-center justify-between text-sm">
        <span className="text-neutral-500">Faculty: {section.faculty_full_name}</span>
        <span className="inline-flex items-center gap-1 text-secondary">
          Moodle link planned
          <ArrowTopRightOnSquareIcon className="h-4 w-4" />
        </span>
      </div>
    </Card>
  )
}
