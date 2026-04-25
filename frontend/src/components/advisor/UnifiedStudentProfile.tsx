import * as Tabs from '@radix-ui/react-tabs'

import { Badge } from '@/components/ui/Badge'
import { Card, CardTitle } from '@/components/ui/Card'
import { DataTable, DataTableBody, DataTableCell, DataTableHead, DataTableHeader, DataTableRow } from '@/components/ui/Table'
import type { AdvisingNote, FinancialFlag, GradeRecord, StudentProfile } from '@/types'
import { formatDate } from '@/utils/formatters'

export function UnifiedStudentProfile({
  grades,
  notes,
  flags,
  student,
}: {
  grades: GradeRecord[]
  notes: AdvisingNote[]
  flags: FinancialFlag[]
  student: StudentProfile
}) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-4">
        <div>
          <CardTitle>{student.full_name}</CardTitle>
          <p className="mt-1 text-sm text-neutral-500">
            {student.student_number} · {student.programme} · Year {student.year_of_study}
          </p>
        </div>
        <Badge tone={student.academic_standing === 'GOOD' ? 'success' : 'warning'}>
          {student.academic_standing}
        </Badge>
      </div>

      <Tabs.Root defaultValue="record" className="mt-6">
        <Tabs.List className="flex flex-wrap gap-2 border-b border-neutral-200 pb-3">
          {['record', 'attendance', 'moodle', 'notes', 'flags'].map((value) => (
            <Tabs.Trigger
              key={value}
              value={value}
              className="rounded-full px-3 py-2 text-sm font-medium text-neutral-500 data-[state=active]:bg-primary data-[state=active]:text-white"
            >
              {value === 'record'
                ? 'Academic Record'
                : value === 'attendance'
                  ? 'Attendance'
                  : value === 'moodle'
                    ? 'Moodle Engagement'
                    : value === 'notes'
                      ? 'Advising Notes'
                      : 'Financial Flags'}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="record" className="mt-4 space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-4">
              <p className="text-sm text-neutral-500">Current GPA</p>
              <p className="mt-2 font-mono text-3xl font-bold text-neutral-900">{student.cumulative_gpa}</p>
            </div>
            <div className="rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-4">
              <p className="text-sm text-neutral-500">Standing</p>
              <p className="mt-2 text-lg font-semibold text-neutral-900">{student.academic_standing}</p>
            </div>
            <div className="rounded-xl border border-neutral-200 bg-neutral-50 px-4 py-4">
              <p className="text-sm text-neutral-500">Attendance flags</p>
              <p className="mt-2 text-lg font-semibold text-neutral-900">
                {student.attendance_percentages.length}
              </p>
            </div>
          </div>
          <DataTable ariaLabel="Student grade table">
            <DataTableHead>
              <tr>
                <DataTableHeader>Course</DataTableHeader>
                <DataTableHeader>Score</DataTableHeader>
                <DataTableHeader>Letter</DataTableHeader>
                <DataTableHeader>Status</DataTableHeader>
              </tr>
            </DataTableHead>
            <DataTableBody>
              {grades.map((grade) => (
                <DataTableRow key={grade.id}>
                  <DataTableCell>{grade.course_title}</DataTableCell>
                  <DataTableCell className="font-mono">{grade.numeric_score ?? '—'}</DataTableCell>
                  <DataTableCell className="font-mono">{grade.letter_grade}</DataTableCell>
                  <DataTableCell>{grade.grade_status}</DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        </Tabs.Content>

        <Tabs.Content value="attendance" className="mt-4 space-y-3">
          {student.attendance_percentages.map((item) => (
            <div key={item.section_id} className="rounded-xl border border-neutral-200 px-4 py-3">
              <div className="flex items-center justify-between">
                <p className="font-mono text-sm text-neutral-700">{item.course_code}</p>
                <p className="text-sm text-neutral-500">{item.attendance_percentage}%</p>
              </div>
              <div className="mt-3 h-1.5 rounded-full bg-neutral-200">
                <div className="h-1.5 rounded-full bg-primary" style={{ width: `${Number(item.attendance_percentage)}%` }} />
              </div>
            </div>
          ))}
        </Tabs.Content>

        <Tabs.Content value="moodle" className="mt-4">
          <p className="text-sm text-neutral-500">
            Moodle engagement is a later integration-phase feed. This tab is reserved so the unified profile
            keeps the correct final structure.
          </p>
        </Tabs.Content>

        <Tabs.Content value="notes" className="mt-4 space-y-3">
          {notes.map((note) => (
            <div key={note.id} className="rounded-xl border border-neutral-200 px-4 py-3">
              <p className="text-sm text-neutral-900">{note.note_text}</p>
              <p className="mt-2 text-xs text-neutral-500">
                {note.status} · {note.created_by_username} · {formatDate(note.created_at)}
              </p>
            </div>
          ))}
        </Tabs.Content>

        <Tabs.Content value="flags" className="mt-4 space-y-3">
          {flags.map((flag) => (
            <div key={flag.id} className="rounded-xl border border-neutral-200 px-4 py-3">
              <p className="font-medium text-neutral-900">{flag.flag_type}</p>
              <p className="mt-1 text-sm text-neutral-600">{flag.reason}</p>
              <p className="mt-2 text-xs text-neutral-500">Effective {formatDate(flag.effective_date)}</p>
            </div>
          ))}
        </Tabs.Content>
      </Tabs.Root>
    </Card>
  )
}
