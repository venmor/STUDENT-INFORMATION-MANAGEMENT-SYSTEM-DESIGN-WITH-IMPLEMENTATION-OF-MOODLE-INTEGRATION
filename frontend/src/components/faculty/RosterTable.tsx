import { DataTable, DataTableBody, DataTableCell, DataTableHead, DataTableHeader, DataTableRow } from '@/components/ui/Table'
import { AttendanceMarker } from '@/components/faculty/AttendanceMarker'
import type { SectionRosterEntry } from '@/types'

export function RosterTable({
  onMarkAttendance,
  roster,
}: {
  onMarkAttendance: (studentUserId: number, status: 'PRESENT' | 'ABSENT' | 'EXCUSED') => void
  roster: SectionRosterEntry[]
}) {
  return (
    <DataTable ariaLabel="Section roster table">
      <DataTableHead>
        <tr>
          <DataTableHeader>Name</DataTableHeader>
          <DataTableHeader>ID</DataTableHeader>
          <DataTableHeader>Programme</DataTableHeader>
          <DataTableHeader>Attendance</DataTableHeader>
        </tr>
      </DataTableHead>
      <DataTableBody>
        {roster.map((student) => (
          <DataTableRow key={student.id}>
            <DataTableCell>{student.full_name}</DataTableCell>
            <DataTableCell className="font-mono">{student.student_number}</DataTableCell>
            <DataTableCell>{student.programme}</DataTableCell>
            <DataTableCell>
              <AttendanceMarker onSelect={(status) => onMarkAttendance(student.user_id, status)} />
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}
