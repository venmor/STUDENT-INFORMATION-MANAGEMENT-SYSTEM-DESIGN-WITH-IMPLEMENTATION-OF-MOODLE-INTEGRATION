import { Card, CardTitle } from '@/components/ui/Card'
import { DataTable, DataTableBody, DataTableCell, DataTableHead, DataTableHeader, DataTableRow } from '@/components/ui/Table'
import { useCourses, useSections } from '@/hooks/useCourses'

export function AdminCoursesPage() {
  const courses = useCourses()
  const sections = useSections()

  return (
    <div className="space-y-6">
      <Card>
        <CardTitle>Course catalog</CardTitle>
        <div className="mt-4">
          <DataTable ariaLabel="Course catalog table">
            <DataTableHead>
              <tr>
                <DataTableHeader>Code</DataTableHeader>
                <DataTableHeader>Title</DataTableHeader>
                <DataTableHeader>Credits</DataTableHeader>
              </tr>
            </DataTableHead>
            <DataTableBody>
              {(courses.data ?? []).map((course) => (
                <DataTableRow key={course.id}>
                  <DataTableCell className="font-mono">{course.course_code}</DataTableCell>
                  <DataTableCell>{course.course_title}</DataTableCell>
                  <DataTableCell className="font-mono">{course.credit_hours}</DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        </div>
      </Card>
      <Card>
        <CardTitle>Sections</CardTitle>
        <div className="mt-4">
          <DataTable ariaLabel="Section table">
            <DataTableHead>
              <tr>
                <DataTableHeader>Course</DataTableHeader>
                <DataTableHeader>Section</DataTableHeader>
                <DataTableHeader>Faculty</DataTableHeader>
              </tr>
            </DataTableHead>
            <DataTableBody>
              {(sections.data ?? []).map((section) => (
                <DataTableRow key={section.id}>
                  <DataTableCell>{section.course_title}</DataTableCell>
                  <DataTableCell className="font-mono">{section.section_code}</DataTableCell>
                  <DataTableCell>{section.faculty_full_name}</DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        </div>
      </Card>
    </div>
  )
}
