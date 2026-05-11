import { Card, CardTitle } from '@/components/ui/Card'
import { EnhancedDataTable, type Column } from '@/components/ui/EnhancedDataTable'
import { useCourses, useSections } from '@/hooks/useCourses'

interface CourseRow {
  id: string
  course_code: string
  course_title: string
  credit_hours: number
  department?: string
}

interface SectionRow {
  id: string
  course_title: string
  section_code: string
  faculty_full_name: string
}

const courseColumns: Column<CourseRow>[] = [
  { key: 'course_code', label: 'Code', sortable: true },
  { key: 'course_title', label: 'Title', sortable: true },
  { key: 'credit_hours', label: 'Credits', sortable: true },
]

const sectionColumns: Column<SectionRow>[] = [
  { key: 'course_title', label: 'Course', sortable: true },
  { key: 'section_code', label: 'Section', sortable: true },
  { key: 'faculty_full_name', label: 'Faculty', sortable: true },
]

export function AdminCoursesPage() {
  const courses = useCourses()
  const sections = useSections()

  return (
    <div className="space-y-6">
      <Card>
        <CardTitle>Course catalog</CardTitle>
        <div className="mt-4">
          <EnhancedDataTable
            data={(courses.data ?? []) as CourseRow[]}
            columns={courseColumns}
            ariaLabel="Course catalog"
            searchableKeys={['course_code', 'course_title']}
          />
        </div>
      </Card>
      <Card>
        <CardTitle>Sections</CardTitle>
        <div className="mt-4">
          <EnhancedDataTable
            data={(sections.data ?? []) as SectionRow[]}
            columns={sectionColumns}
            ariaLabel="Section list"
            searchableKeys={['course_title', 'section_code', 'faculty_full_name']}
          />
        </div>
      </Card>
    </div>
  )
}
