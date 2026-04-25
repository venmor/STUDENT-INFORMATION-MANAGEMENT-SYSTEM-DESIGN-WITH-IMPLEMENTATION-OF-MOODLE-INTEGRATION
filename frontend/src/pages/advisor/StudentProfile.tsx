import { UserCircleIcon } from '@heroicons/react/24/outline'
import { useParams } from 'react-router-dom'

import { AdvisingNoteEditor } from '@/components/advisor/AdvisingNoteEditor'
import { AISummarisationPanel } from '@/components/advisor/AISummarisationPanel'
import { UnifiedStudentProfile } from '@/components/advisor/UnifiedStudentProfile'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useGrades } from '@/hooks/useGrades'
import { useAdvisingNotes, useFinancialFlags, useStudent, useStudentMutations } from '@/hooks/useStudents'

export function AdvisorStudentProfilePage() {
  const { studentId } = useParams()
  const student = useStudent(studentId)
  const notes = useAdvisingNotes(studentId)
  const flags = useFinancialFlags(studentId)
  const grades = useGrades({ studentId })
  const mutations = useStudentMutations(studentId)

  if (student.isPending) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-96" />
        <Skeleton className="h-48" />
        <Skeleton className="h-56" />
      </div>
    )
  }

  if (!student.data) {
    return (
      <EmptyState
        icon={<UserCircleIcon className="h-12 w-12" />}
        title="Student profile unavailable"
        description="The requested advisee record could not be loaded. Return to the advisor dashboard and try another student."
      />
    )
  }

  return (
    <div className="space-y-6">
      <UnifiedStudentProfile
        student={student.data}
        grades={grades.data ?? []}
        notes={notes.data ?? []}
        flags={flags.data ?? []}
      />
      <Card>
        <CardTitle>New advising note</CardTitle>
        <div className="mt-4">
          <AdvisingNoteEditor
            isPending={mutations.createAdvisingNote.isPending}
            onSave={(value) => mutations.createAdvisingNote.mutate(value)}
          />
        </div>
      </Card>
      <AISummarisationPanel />
    </div>
  )
}
