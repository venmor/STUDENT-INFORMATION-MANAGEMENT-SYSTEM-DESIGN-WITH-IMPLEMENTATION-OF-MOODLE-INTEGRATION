import { ClipboardDocumentCheckIcon } from '@heroicons/react/24/outline'

import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { GradeHistoryTable } from '@/components/student/GradeHistoryTable'
import { Skeleton } from '@/components/ui/Skeleton'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import { useGrades } from '@/hooks/useGrades'

export function StudentGradesPage() {
  const user = useCurrentUser()
  const grades = useGrades({ studentId: user?.studentProfileId ?? undefined })

  return (
    <Card>
      <CardTitle>Official grades</CardTitle>
      <div className="mt-4">
        {grades.isPending ? (
          <div className="space-y-3">
            <Skeleton className="h-10" />
            <Skeleton className="h-10" />
            <Skeleton className="h-10" />
          </div>
        ) : grades.data?.length ? (
          <GradeHistoryTable grades={grades.data} />
        ) : (
          <EmptyState
            icon={<ClipboardDocumentCheckIcon className="h-12 w-12" />}
            title="No official grades yet"
            description="Grades will appear here after they are entered and officialised through the academic workflow."
          />
        )}
      </div>
    </Card>
  )
}
