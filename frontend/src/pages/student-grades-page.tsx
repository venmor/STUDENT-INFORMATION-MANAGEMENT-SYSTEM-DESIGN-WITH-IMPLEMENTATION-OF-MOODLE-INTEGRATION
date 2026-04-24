import { useQuery } from '@tanstack/react-query'

import { getGrades } from '@/api/academics'
import { downloadTranscript } from '@/api/students'
import { useAuth } from '@/auth/auth-context'
import { DataState } from '@/components/ui/data-state'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'
import { formatDateTime, formatDecimal } from '@/utils/format'

function triggerBrowserDownload(blob: Blob, filename: string) {
  const objectUrl = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = objectUrl
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(objectUrl)
}

export default function StudentGradesPage() {
  const { session } = useAuth()
  const studentId = session?.user.studentProfileId
  const gradesQuery = useQuery({
    queryKey: ['grades', 'student-official'],
    queryFn: () => getGrades(),
  })

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Student grades"
        title="Official grade history"
        description="Only official grades are visible here. Draft grades remain hidden until admin release."
        actions={
          <button
            type="button"
            onClick={async () => {
              if (!studentId) {
                return
              }
              const transcript = await downloadTranscript(studentId)
              triggerBrowserDownload(transcript, `transcript-${studentId}.pdf`)
            }}
            disabled={!studentId}
            className="min-h-11 rounded-2xl border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/16 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Download transcript
          </button>
        }
      />

      <Panel title="Grade table" description="This view reads the official-only grade list for the authenticated student.">
        {gradesQuery.isLoading ? (
          <DataState title="Loading grades" message="Fetching official grade records." />
        ) : gradesQuery.isError ? (
          <DataState title="Grade load failed" message="The grade list could not be loaded from the backend." />
        ) : gradesQuery.data && gradesQuery.data.length ? (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm text-slate-700">
              <thead className="text-xs uppercase tracking-[0.24em] text-slate-500">
                <tr>
                  <th className="pb-3">Course</th>
                  <th className="pb-3">Section</th>
                  <th className="pb-3">Score</th>
                  <th className="pb-3">Letter</th>
                  <th className="pb-3">Points</th>
                  <th className="pb-3">Released</th>
                </tr>
              </thead>
              <tbody>
                {gradesQuery.data.map((grade) => (
                  <tr key={grade.id} className="border-t border-slate-200">
                    <td className="py-3">
                      <div className="font-semibold text-slate-900">{grade.course_code}</div>
                      <div className="text-slate-600">{grade.course_title}</div>
                    </td>
                    <td className="py-3">{grade.section_code}</td>
                    <td className="py-3">{grade.numeric_score ?? grade.special_code}</td>
                    <td className="py-3">{grade.letter_grade}</td>
                    <td className="py-3">{formatDecimal(grade.grade_points)}</td>
                    <td className="py-3">{formatDateTime(grade.officialised_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <DataState title="No official grades" message="No official grade records are available yet." />
        )}
      </Panel>
    </div>
  )
}
