import { useMemo } from 'react'
import { ArrowDownTrayIcon, ClipboardDocumentCheckIcon } from '@heroicons/react/24/outline'

import { downloadExamSlip, downloadResultsSlip } from '@/api/grades'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { DataTable, DataTableBody, DataTableCell, DataTableHead, DataTableHeader, DataTableRow } from '@/components/ui/Table'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import { useGrades } from '@/hooks/useGrades'
import type { GradeRecord } from '@/types'

interface SemesterGroup {
  key: string
  semester: string
  academicYear: string
  grades: GradeRecord[]
  semesterGpa: string
}

function groupBySemester(grades: GradeRecord[]): SemesterGroup[] {
  const map = new Map<string, GradeRecord[]>()
  for (const g of grades) {
    const key = `${g.academic_year}|${g.semester}`
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(g)
  }
  return Array.from(map.entries()).map(([key, semGrades]) => {
    let totalQualityPoints = 0
    let totalCredits = 0
    for (const g of semGrades) {
      if (g.special_code === 'I') continue
      const credits = g.credit_hours || 0
      totalQualityPoints += parseFloat(g.grade_points) * credits
      totalCredits += credits
    }
    const gpa = totalCredits > 0 ? (totalQualityPoints / totalCredits).toFixed(2) : '0.00'
    return {
      key,
      semester: semGrades[0].semester,
      academicYear: semGrades[0].academic_year,
      grades: semGrades,
      semesterGpa: gpa,
    }
  })
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export function StudentGradesPage() {
  const user = useCurrentUser()
  const grades = useGrades({ studentId: user?.studentProfileId ?? undefined })

  const semesters = useMemo(() => groupBySemester(grades.data || []), [grades.data])

  async function handleDownloadExamSlip(semester: string, academicYear: string) {
    if (!user?.studentProfileId) return
    const blob = await downloadExamSlip(user.studentProfileId, semester, academicYear)
    triggerDownload(blob, `exam-slip-${semester}-${academicYear}.pdf`)
  }

  async function handleDownloadResultsSlip(semester: string, academicYear: string) {
    if (!user?.studentProfileId) return
    const blob = await downloadResultsSlip(user.studentProfileId, semester, academicYear)
    triggerDownload(blob, `results-slip-${semester}-${academicYear}.pdf`)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardTitle>Official Grades</CardTitle>
        <div className="mt-4">
          {grades.isPending ? (
            <div className="space-y-3">
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
            </div>
          ) : !grades.data?.length ? (
            <EmptyState
              icon={<ClipboardDocumentCheckIcon className="h-12 w-12" />}
              title="No official grades yet"
              description="Grades will appear here after they are entered and officialised through the academic workflow."
            />
          ) : (
            <div className="space-y-8">
              {semesters.map((sem) => (
                <div key={sem.key}>
                  <div className="mb-3 flex items-center justify-between">
                    <div>
                      <h3 className="font-display text-sm font-bold text-neutral-900">
                        {sem.semester} — {sem.academicYear}
                      </h3>
                      <p className="text-xs text-neutral-500">
                        Semester GPA: <span className="font-mono font-bold">{sem.semesterGpa}</span>
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDownloadExamSlip(sem.semester, sem.academicYear)}
                      >
                        <ArrowDownTrayIcon className="mr-1 h-3.5 w-3.5" />
                        Exam Slip
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDownloadResultsSlip(sem.semester, sem.academicYear)}
                      >
                        <ArrowDownTrayIcon className="mr-1 h-3.5 w-3.5" />
                        Results Slip
                      </Button>
                    </div>
                  </div>
                  <DataTable ariaLabel={`Grades for ${sem.semester} ${sem.academicYear}`}>
                    <DataTableHead>
                      <tr>
                        <DataTableHeader>Course</DataTableHeader>
                        <DataTableHeader>Credits</DataTableHeader>
                        <DataTableHeader>CA</DataTableHeader>
                        <DataTableHeader>Exam</DataTableHeader>
                        <DataTableHeader>Total</DataTableHeader>
                        <DataTableHeader>Grade</DataTableHeader>
                        <DataTableHeader>Status</DataTableHeader>
                      </tr>
                    </DataTableHead>
                    <DataTableBody>
                      {sem.grades.map((grade) => (
                        <DataTableRow key={grade.id}>
                          <DataTableCell>
                            <div>
                              <p className="font-mono text-xs text-neutral-500">{grade.course_code}</p>
                              <p className="text-sm">{grade.course_title}</p>
                            </div>
                          </DataTableCell>
                          <DataTableCell className="font-mono text-sm">{grade.credit_hours}</DataTableCell>
                          <DataTableCell className="font-mono text-sm">{grade.ca_score ?? '—'}</DataTableCell>
                          <DataTableCell className="font-mono text-sm">{grade.exam_score ?? '—'}</DataTableCell>
                          <DataTableCell className="font-mono text-sm">{grade.numeric_score ?? '—'}</DataTableCell>
                          <DataTableCell className="font-mono text-sm font-bold">{grade.letter_grade || '—'}</DataTableCell>
                          <DataTableCell>
                            <Badge tone={grade.grade_status === 'OFFICIAL' ? 'success' : 'warning'}>
                              {grade.grade_status}
                            </Badge>
                          </DataTableCell>
                        </DataTableRow>
                      ))}
                    </DataTableBody>
                  </DataTable>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
