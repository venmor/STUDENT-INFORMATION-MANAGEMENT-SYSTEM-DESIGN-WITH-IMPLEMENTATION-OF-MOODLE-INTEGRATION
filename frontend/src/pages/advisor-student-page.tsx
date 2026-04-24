import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useParams } from 'react-router-dom'

import { getGrades } from '@/api/academics'
import {
  createAdvisingNote,
  getAdvisingNotes,
  getFinancialFlags,
  getStudent,
  updateAdvisingNote,
} from '@/api/students'
import { DataState } from '@/components/ui/data-state'
import { MetricStrip } from '@/components/ui/metric-strip'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'
import { RoadmapPanel } from '@/components/ui/roadmap-panel'
import { formatDateTime } from '@/utils/format'

export default function AdvisorStudentPage() {
  const { studentId = '' } = useParams()
  const queryClient = useQueryClient()
  const [draftNote, setDraftNote] = useState('')
  const [message, setMessage] = useState('')
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null)
  const [editingNoteText, setEditingNoteText] = useState('')

  const studentQuery = useQuery({
    queryKey: ['student', studentId, 'advisor-profile'],
    queryFn: () => getStudent(studentId),
  })
  const flagsQuery = useQuery({
    queryKey: ['financial-flags', studentId],
    queryFn: () => getFinancialFlags(studentId),
  })
  const gradesQuery = useQuery({
    queryKey: ['grades', studentId, 'advisor-profile'],
    queryFn: () => getGrades({ studentId }),
  })
  const notesQuery = useQuery({
    queryKey: ['advising-notes', studentId],
    queryFn: () => getAdvisingNotes(studentId),
  })

  const createNoteMutation = useMutation({
    mutationFn: ({ studentId, noteText }: { studentId: string; noteText: string }) =>
      createAdvisingNote(studentId, noteText),
    onSuccess: async () => {
      setDraftNote('')
      setMessage('Advising note saved as draft.')
      await queryClient.invalidateQueries({ queryKey: ['advising-notes', studentId] })
    },
    onError: () => {
      setMessage('Advising note save failed.')
    },
  })

  const updateNoteMutation = useMutation({
    mutationFn: ({ studentId, noteId, noteText }: { studentId: string; noteId: string; noteText: string }) =>
      updateAdvisingNote(studentId, noteId, noteText),
    onSuccess: async () => {
      setEditingNoteId(null)
      setEditingNoteText('')
      setMessage('Draft advising note updated.')
      await queryClient.invalidateQueries({ queryKey: ['advising-notes', studentId] })
    },
    onError: () => {
      setMessage('Draft advising note update failed.')
    },
  })

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Advisor profile"
        title={studentQuery.data?.full_name ?? 'Unified student profile'}
        description="This page combines the student record, attendance, financial flags, official grade history, and advising notes for assigned students."
      />

      <MetricStrip
        items={[
          {
            label: 'Standing',
            value: studentQuery.data?.academic_standing ?? 'Unknown',
          },
          {
            label: 'GPA',
            value: studentQuery.data?.cumulative_gpa ?? '0.00',
            accent: 'text-teal-700',
          },
          {
            label: 'Financial flags',
            value: String(flagsQuery.data?.length ?? 0),
          },
          {
            label: 'Official grades',
            value: String(gradesQuery.data?.length ?? 0),
          },
        ]}
      />

      <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-5">
          <Panel title="Student record" description="Pulled directly from the student detail endpoint.">
            {studentQuery.isLoading ? (
              <DataState title="Loading profile" message="Fetching the student profile." />
            ) : studentQuery.isError || !studentQuery.data ? (
              <DataState title="Profile load failed" message="The student profile could not be loaded." />
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Identity</p>
                  <p className="mt-3 text-lg font-semibold text-slate-900">{studentQuery.data.full_name}</p>
                  <p className="mt-1 text-sm text-slate-600">{studentQuery.data.student_number}</p>
                  <p className="mt-1 text-sm text-slate-600">{studentQuery.data.programme}</p>
                </div>
                <div className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Attendance</p>
                  {studentQuery.data.attendance_percentages.length ? (
                    <ul className="mt-3 space-y-2 text-sm text-slate-700">
                      {studentQuery.data.attendance_percentages.map((row) => (
                        <li key={row.section_id}>
                          {row.course_code}: {row.attendance_percentage}% / {row.threshold}%
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-3 text-sm text-slate-600">No attendance data yet.</p>
                  )}
                </div>
              </div>
            )}
          </Panel>

          <Panel title="Official grade history" description="Advisor access is limited to official grades only.">
            {gradesQuery.isLoading ? (
              <DataState title="Loading grades" message="Fetching the student's official grade history." />
            ) : gradesQuery.isError ? (
              <DataState title="Grade load failed" message="Official grade history could not be loaded." />
            ) : gradesQuery.data && gradesQuery.data.length ? (
              <div className="overflow-x-auto">
                <table className="min-w-full text-left text-sm text-slate-700">
                  <thead className="text-xs uppercase tracking-[0.24em] text-slate-500">
                    <tr>
                      <th className="pb-3">Course</th>
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
                        <td className="py-3">{grade.letter_grade}</td>
                        <td className="py-3">{grade.grade_points}</td>
                        <td className="py-3">{formatDateTime(grade.officialised_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <DataState title="No official grades" message="No official grades are available for this student yet." />
            )}
          </Panel>
        </div>

        <div className="space-y-5">
          <Panel title="Financial flags" description="Visible to advisors so registration and intervention decisions can be made in context.">
            {flagsQuery.isLoading ? (
              <DataState title="Loading flags" message="Fetching financial flags." />
            ) : flagsQuery.isError ? (
              <DataState title="Flag load failed" message="Financial flags could not be loaded." />
            ) : flagsQuery.data && flagsQuery.data.length ? (
              <div className="space-y-3">
                {flagsQuery.data.map((flag) => (
                  <article key={flag.id} className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                    <p className="text-sm font-semibold text-slate-900">{flag.flag_type}</p>
                    <p className="mt-2 text-sm text-slate-600">{flag.reason}</p>
                  </article>
                ))}
              </div>
            ) : (
              <DataState title="No flags" message="No financial flags are currently active." />
            )}
          </Panel>

          <Panel title="Advising notes" description="Draft notes remain editable until they are approved by admin.">
            <form
              className="mb-4 grid gap-3"
              onSubmit={(event) => {
                event.preventDefault()
                setMessage('')
                createNoteMutation.mutate({ studentId, noteText: draftNote })
              }}
            >
              <textarea
                value={draftNote}
                onChange={(event) => setDraftNote(event.target.value)}
                rows={4}
                placeholder="Add a new advising note"
                className="rounded-2xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-slate-900"
                required
              />
              {message ? <p className="text-sm text-slate-700">{message}</p> : null}
              <button
                type="submit"
                disabled={createNoteMutation.isPending}
                className="min-h-11 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {createNoteMutation.isPending ? 'Saving...' : 'Save draft note'}
              </button>
            </form>

            {notesQuery.isLoading ? (
              <DataState title="Loading notes" message="Fetching advising notes." />
            ) : notesQuery.isError ? (
              <DataState title="Note load failed" message="Advising notes could not be loaded." />
            ) : notesQuery.data && notesQuery.data.length ? (
              <div className="space-y-3">
                {notesQuery.data.map((note) => (
                  <article key={note.id} className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <p className="text-sm font-semibold text-slate-900">{note.status}</p>
                      <p className="text-xs text-slate-500">Created {formatDateTime(note.created_at)}</p>
                    </div>
                    {editingNoteId === note.id ? (
                      <form
                        className="mt-3 grid gap-3"
                        onSubmit={(event) => {
                          event.preventDefault()
                          updateNoteMutation.mutate({
                            studentId,
                            noteId: note.id,
                            noteText: editingNoteText,
                          })
                        }}
                      >
                        <textarea
                          value={editingNoteText}
                          onChange={(event) => setEditingNoteText(event.target.value)}
                          rows={4}
                          className="rounded-2xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-slate-900"
                        />
                        <div className="flex gap-3">
                          <button
                            type="submit"
                            className="min-h-11 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                          >
                            Save update
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setEditingNoteId(null)
                              setEditingNoteText('')
                            }}
                            className="min-h-11 rounded-2xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700"
                          >
                            Cancel
                          </button>
                        </div>
                      </form>
                    ) : (
                      <>
                        <p className="mt-3 text-sm text-slate-700">{note.note_text}</p>
                        {note.status !== 'APPROVED' ? (
                          <button
                            type="button"
                            onClick={() => {
                              setEditingNoteId(note.id)
                              setEditingNoteText(note.note_text)
                            }}
                            className="mt-3 min-h-11 rounded-2xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700"
                          >
                            Edit draft
                          </button>
                        ) : null}
                      </>
                    )}
                  </article>
                ))}
              </div>
            ) : (
              <DataState title="No notes" message="No advising notes have been recorded yet." />
            )}
          </Panel>

          <RoadmapPanel
            title="Moodle engagement"
            requirement="FR-STU-006"
            description="Advisor Moodle engagement data is reserved here for the later Moodle integration phase."
          />
        </div>
      </div>
    </div>
  )
}
