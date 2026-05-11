import { Link } from 'react-router-dom'

import { Badge } from '@/components/ui/Badge'
import { Card, CardTitle } from '@/components/ui/Card'
import type { StudentProfile } from '@/types'
import { formatGpa } from '@/utils/formatters'

export function QuickStatsPanel({ student }: { student: StudentProfile }) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Link to="/student/grades">
        <Card interactive>
          <CardTitle>Current GPA</CardTitle>
          <p className="mt-3 font-mono text-4xl font-bold text-neutral-900">
            {formatGpa(student.cumulative_gpa)}
          </p>
        </Card>
      </Link>
      <Link to="/student/grades">
        <Card interactive>
          <CardTitle>Standing</CardTitle>
          <div className="mt-4">
            <Badge tone={student.academic_standing === 'GOOD' ? 'success' : 'warning'}>
              {student.academic_standing}
            </Badge>
          </div>
        </Card>
      </Link>
      <Link to="/student/courses">
        <Card interactive>
          <CardTitle>Year of study</CardTitle>
          <p className="mt-3 font-mono text-4xl font-bold text-neutral-900">{student.year_of_study}</p>
        </Card>
      </Link>
    </div>
  )
}
