import { AcademicCapIcon } from '@heroicons/react/24/outline'

import { Badge } from '@/components/ui/Badge'
import { DataTable, DataTableBody, DataTableCell, DataTableHead, DataTableHeader, DataTableRow, EmptyState } from '@/components/ui/Table'
import type { GradeRecord } from '@/types'

export function GradeHistoryTable({ grades }: { grades: GradeRecord[] }) {
  if (!grades.length) {
    return (
      <EmptyState
        icon={<AcademicCapIcon className="h-12 w-12" />}
        title="No grades found"
        description="Official grade records will appear here as soon as they are released."
      />
    )
  }

  return (
    <DataTable ariaLabel="Grade history table">
      <DataTableHead>
        <tr>
          <DataTableHeader>Course</DataTableHeader>
          <DataTableHeader>Section</DataTableHeader>
          <DataTableHeader>Score</DataTableHeader>
          <DataTableHeader>Letter</DataTableHeader>
          <DataTableHeader>Status</DataTableHeader>
        </tr>
      </DataTableHead>
      <DataTableBody>
        {grades.map((grade) => (
          <DataTableRow key={grade.id}>
            <DataTableCell>
              <div>
                <p className="font-mono text-xs text-neutral-500">{grade.course_code}</p>
                <p>{grade.course_title}</p>
              </div>
            </DataTableCell>
            <DataTableCell className="font-mono">{grade.section_code}</DataTableCell>
            <DataTableCell className="font-mono">{grade.numeric_score ?? '—'}</DataTableCell>
            <DataTableCell className="font-mono">{grade.letter_grade || '—'}</DataTableCell>
            <DataTableCell>
              <Badge tone={grade.grade_status === 'OFFICIAL' ? 'success' : 'warning'}>
                {grade.grade_status}
              </Badge>
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}
