import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'

import { createGrade, getGrades, getSection, getSectionRoster } from '@/api/academics'
import { DataState } from '@/components/ui/data-state'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'

export default function FacultySectionPage() {
  const { sectionId = '' } = useParams()
  const queryClient = useQueryClient()
  const [drafts, setDrafts] = useState<Record<string, { numericScore: string; specialCode: string }>>({})
  const [message, setMessage] = useState('')

  const sectionQuery = useQuery({
    queryKey: ['section', sectionId, 'faculty-detail'],
    queryFn: () => getSection(sectionId),
  })
  const rosterQuery = useQuery({
    queryKey: ['section-roster', sectionId],
    queryFn: () => getSectionRoster(sectionId),
  })
  const gradesQuery = useQuery({
    queryKey: ['grades', 'faculty', sectionId],
    queryFn: () => getGrades(),
  })

  const gradeMutation = useMutation({
    mutationFn: createGrade,
    onSuccess: async () => {
      setMessage('Draft grade saved.')
      await queryClient.invalidateQueries({ queryKey: ['grades', 'faculty', sectionId] })
    },
    onError: () => {
      setMessage('Draft grade save failed.')
    },
  })

  const gradesByStudentUserId = useMemo(() => {
    return new Map(
      (gradesQuery.data ?? [])
        .filter((grade) => grade.section_id === sectionId)
        .map((grade) => [grade.student_id, grade]),
    )
  }, [gradesQuery.data, sectionId])

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Faculty section"
        title={
          sectionQuery.data
            ? `${sectionQuery.data.course_code} · Section ${sectionQuery.data.section_code}`
            : 'Section roster'
        }
        description="Roster entries and grade submission are scoped to the currently assigned faculty user."
      />

      <Panel title="Roster and draft grades" description="Grade entry uses the grade create endpoint, which upserts draft grades for enrolled students.">
        {rosterQuery.isLoading || sectionQuery.isLoading ? (
          <DataState title="Loading roster" message="Fetching the section roster and existing draft grades." />
        ) : rosterQuery.isError || sectionQuery.isError ? (
          <DataState title="Roster load failed" message="The section roster could not be loaded." />
        ) : rosterQuery.data && rosterQuery.data.length ? (
          <div className="space-y-4">
            {message ? (
              <div className="rounded-2xl border border-teal-200 bg-teal-50 px-4 py-3 text-sm text-teal-800">
                {message}
              </div>
            ) : null}
            {rosterQuery.data.map((student) => {
              const draft = drafts[student.user_id] ?? { numericScore: '', specialCode: '' }
              const existingGrade = gradesByStudentUserId.get(student.student_id)
              return (
                <article key={student.id} className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-lg font-semibold text-slate-900">{student.full_name}</p>
                      <p className="mt-1 text-sm text-slate-600">{student.student_number}</p>
                    </div>
                    <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                      {existingGrade ? existingGrade.letter_grade : 'No draft'}
                    </div>
                  </div>

                  <form
                    className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_auto]"
                    onSubmit={(event) => {
                      event.preventDefault()
                      setMessage('')
                      gradeMutation.mutate({
                        studentUserId: student.user_id,
                        sectionId,
                        numericScore: draft.numericScore || undefined,
                        specialCode: draft.specialCode || undefined,
                      })
                    }}
                  >
                    <label className="grid gap-2 text-sm text-slate-700">
                      <span>Numeric score</span>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        step="0.01"
                        value={draft.numericScore}
                        onChange={(event) =>
                          setDrafts((current) => ({
                            ...current,
                            [student.user_id]: {
                              ...draft,
                              numericScore: event.target.value,
                            },
                          }))
                        }
                        className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
                      />
                    </label>
                    <label className="grid gap-2 text-sm text-slate-700">
                      <span>Special code</span>
                      <select
                        value={draft.specialCode}
                        onChange={(event) =>
                          setDrafts((current) => ({
                            ...current,
                            [student.user_id]: {
                              ...draft,
                              specialCode: event.target.value,
                            },
                          }))
                        }
                        className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
                      >
                        <option value="">None</option>
                        <option value="I">I</option>
                        <option value="W">W</option>
                      </select>
                    </label>
                    <button
                      type="submit"
                      disabled={gradeMutation.isPending}
                      className="mt-6 min-h-11 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
                    >
                      {gradeMutation.isPending ? 'Saving...' : 'Save draft'}
                    </button>
                  </form>
                </article>
              )
            })}
          </div>
        ) : (
          <DataState title="No roster entries" message="No enrolled students are currently in this section." />
        )}
      </Panel>
    </div>
  )
}
