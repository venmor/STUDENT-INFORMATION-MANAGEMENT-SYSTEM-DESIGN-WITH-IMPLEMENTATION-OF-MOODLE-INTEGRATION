import { useMemo } from 'react'
import { AcademicCapIcon } from '@heroicons/react/24/outline'
import { useNavigate, useParams } from 'react-router-dom'

import { InlineGradeEntry } from '@/components/faculty/InlineGradeEntry'
import { RosterTable } from '@/components/faculty/RosterTable'
import { SectionTabs } from '@/components/faculty/SectionTabs'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import { useSections } from '@/hooks/useCourses'
import { useSectionRoster } from '@/hooks/useEnrollments'
import { useGradeMutations } from '@/hooks/useGrades'

export function FacultySectionDetailPage() {
  const navigate = useNavigate()
  const user = useCurrentUser()
  const { sectionId } = useParams()
  const sections = useSections()
  const assignedSections = useMemo(
    () => (sections.data ?? []).filter((section) => section.faculty_user_id === user?.id),
    [sections.data, user?.id],
  )
  const activeSectionId = sectionId ?? assignedSections[0]?.id ?? ''
  const roster = useSectionRoster(activeSectionId)
  const grades = useGradeMutations()

  if (!assignedSections.length) {
    return (
      <EmptyState
        icon={<AcademicCapIcon className="h-12 w-12" />}
        title="No faculty section selected"
        description="There are no assigned sections available for roster and grade work in the current account context."
      />
    )
  }

  return (
    <div className="space-y-6">
      <SectionTabs
        sections={assignedSections}
        value={activeSectionId}
        onChange={(nextSectionId) => navigate(`/faculty/sections/${nextSectionId}`)}
      />
      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardTitle>Roster</CardTitle>
          <div className="mt-4">
            <RosterTable roster={roster.data ?? []} onMarkAttendance={() => {}} />
          </div>
        </Card>
        <Card>
          <CardTitle>Draft grade entry</CardTitle>
          <div className="mt-4">
            <InlineGradeEntry
              onSubmit={(payload) =>
                grades.createGrade.mutate({
                  sectionId: activeSectionId,
                  numericScore: payload.numericScore,
                  studentUserId: payload.studentUserId,
                })
              }
            />
          </div>
        </Card>
      </div>
    </div>
  )
}
