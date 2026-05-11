import { RectangleStackIcon } from '@heroicons/react/24/outline'

import { CourseCard } from '@/components/student/CourseCard'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import { useEnrollments } from '@/hooks/useEnrollments'

export function StudentCoursesPage() {
  const user = useCurrentUser()
  const enrollments = useEnrollments({ studentId: user?.studentProfileId ?? undefined })

  return (
    <Card>
      <CardTitle>Active course enrollments</CardTitle>
      <div className="mt-4">
        {enrollments.isPending ? (
          <div className="grid gap-4 lg:grid-cols-2">
            <Skeleton className="h-48" />
            <Skeleton className="h-48" />
          </div>
        ) : enrollments.data?.length ? (
          <div className="grid gap-4 lg:grid-cols-2">
            {enrollments.data.map((enrollment) => (
              <CourseCard key={enrollment.id} enrollment={enrollment} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<RectangleStackIcon className="h-12 w-12" />}
            title="No enrollments found"
            description="You do not have any active section registrations in the current view."
          />
        )}
      </div>
    </Card>
  )
}
