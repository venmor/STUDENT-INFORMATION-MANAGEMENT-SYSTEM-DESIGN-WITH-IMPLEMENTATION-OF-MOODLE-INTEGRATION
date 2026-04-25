import { EnrollmentWizard } from '@/components/student/EnrollmentWizard'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import { useSections } from '@/hooks/useCourses'
import { useEnrollmentMutations, useEnrollments } from '@/hooks/useEnrollments'

export function StudentCourseRegistrationPage() {
  const user = useCurrentUser()
  const sections = useSections()
  const enrollments = useEnrollments({ studentId: user?.studentProfileId ?? undefined })
  const mutations = useEnrollmentMutations()

  return (
    <EnrollmentWizard
      sections={sections.data ?? []}
      enrollments={enrollments.data ?? []}
      isSubmitting={mutations.createEnrollment.isPending || mutations.dropEnrollment.isPending}
      onEnroll={(sectionId) =>
        mutations.createEnrollment.mutate({
          sectionId,
          studentUserId: user?.id,
        })
      }
      onDrop={(enrollmentId) => mutations.dropEnrollment.mutate({ enrollmentId, reason: 'Dropped from portal' })}
    />
  )
}
