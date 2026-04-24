import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useParams } from 'react-router-dom'

import { getGrades, officialiseGrade, updateGrade } from '@/api/academics'
import {
  approveAdvisingNote,
  createFinancialFlag,
  getAdvisingNotes,
  getCorrectionRequests,
  getFinancialFlags,
  getStudent,
  reviewCorrectionRequest,
  updateFinancialFlag,
  updateStudent,
} from '@/api/students'
import { DataState } from '@/components/ui/data-state'
import { MetricStrip } from '@/components/ui/metric-strip'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'

export default function AdminStudentPage() {
  const { studentId = '' } = useParams()
  const queryClient = useQueryClient()
  const [flagForm, setFlagForm] = useState({
    flagType: 'ACCOUNT_HOLD',
    reason: '',
    effectiveDate: '',
  })
  const [standingForm, setStandingForm] = useState({
    academicStanding: 'GOOD',
    standingOverrideReason: '',
  })
  const [message, setMessage] = useState('')

  const studentQuery = useQuery({
    queryKey: ['student', studentId, 'admin-detail'],
    queryFn: () => getStudent(studentId),
  })
  const flagsQuery = useQuery({
    queryKey: ['financial-flags', studentId, 'admin-detail'],
    queryFn: () => getFinancialFlags(studentId),
  })
  const notesQuery = useQuery({
    queryKey: ['advising-notes', studentId, 'admin-detail'],
    queryFn: () => getAdvisingNotes(studentId),
  })
  const correctionsQuery = useQuery({
    queryKey: ['correction-requests', studentId, 'admin-detail'],
    queryFn: () => getCorrectionRequests(studentId),
  })
  const gradesQuery = useQuery({
    queryKey: ['grades', studentId, 'admin-detail'],
    queryFn: () => getGrades({ studentId }),
  })

  const createFlagMutation = useMutation({
    mutationFn: ({
      studentId,
      payload,
    }: {
      studentId: string
      payload: { flagType: string; reason: string; effectiveDate: string }
    }) => createFinancialFlag(studentId, payload),
    onSuccess: async () => {
      setMessage('Financial flag created.')
      setFlagForm({ flagType: 'ACCOUNT_HOLD', reason: '', effectiveDate: '' })
      await queryClient.invalidateQueries({ queryKey: ['financial-flags', studentId] })
    },
  })

  const clearFlagMutation = useMutation({
    mutationFn: ({
      studentId,
      flagId,
      payload,
    }: {
      studentId: string
      flagId: string
      payload: { reason?: string; clearedDate?: string | null }
    }) => updateFinancialFlag(studentId, flagId, payload),
    onSuccess: async () => {
      setMessage('Financial flag updated.')
      await queryClient.invalidateQueries({ queryKey: ['financial-flags', studentId] })
    },
  })

  const approveNoteMutation = useMutation({
    mutationFn: ({ studentId, noteId }: { studentId: string; noteId: string }) =>
      approveAdvisingNote(studentId, noteId),
    onSuccess: async () => {
      setMessage('Advising note approved.')
      await queryClient.invalidateQueries({ queryKey: ['advising-notes', studentId] })
    },
  })

  const reviewCorrectionMutation = useMutation({
    mutationFn: ({
      studentId,
      correctionRequestId,
      payload,
    }: {
      studentId: string
      correctionRequestId: string
      payload: { status: string; reviewNote: string }
    }) => reviewCorrectionRequest(studentId, correctionRequestId, payload),
    onSuccess: async () => {
      setMessage('Correction request reviewed.')
      await queryClient.invalidateQueries({ queryKey: ['correction-requests', studentId] })
    },
  })

  const officialiseMutation = useMutation({
    mutationFn: officialiseGrade,
    onSuccess: async () => {
      setMessage('Grade officialised.')
      await queryClient.invalidateQueries({ queryKey: ['grades', studentId] })
      await queryClient.invalidateQueries({ queryKey: ['student', studentId] })
    },
  })

  const standingMutation = useMutation({
    mutationFn: ({
      studentId,
      payload,
    }: {
      studentId: string
      payload: { academicStanding?: string; standingOverrideReason?: string }
    }) => updateStudent(studentId, payload),
    onSuccess: async () => {
      setMessage('Student standing updated.')
      await queryClient.invalidateQueries({ queryKey: ['student', studentId] })
    },
  })

  const gradeUpdateMutation = useMutation({
    mutationFn: ({
      gradeId,
      payload,
    }: {
      gradeId: string
      payload: { numericScore?: string; specialCode?: string; changeReason?: string }
    }) => updateGrade(gradeId, payload),
    onSuccess: async () => {
      setMessage('Grade updated.')
      await queryClient.invalidateQueries({ queryKey: ['grades', studentId] })
    },
  })

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Admin student operations"
        title={studentQuery.data?.full_name ?? 'Student operations'}
        description="Admins can manage student standing, financial flags, advising-note approval, correction request review, and grade release from one place."
      />

      <MetricStrip
        items={[
          { label: 'Flags', value: String(flagsQuery.data?.length ?? 0) },
          { label: 'Notes', value: String(notesQuery.data?.length ?? 0) },
          { label: 'Corrections', value: String(correctionsQuery.data?.length ?? 0) },
          { label: 'Grades', value: String(gradesQuery.data?.length ?? 0) },
        ]}
      />

      <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <Panel title="Standing override" description="The backend requires an explicit reason whenever academic standing changes.">
          <form
            className="grid gap-4"
            onSubmit={(event) => {
              event.preventDefault()
              standingMutation.mutate({
                studentId,
                payload: standingForm,
              })
            }}
          >
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Academic standing</span>
              <select
                value={standingForm.academicStanding}
                onChange={(event) =>
                  setStandingForm((current) => ({ ...current, academicStanding: event.target.value }))
                }
                className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
              >
                <option value="GOOD">GOOD</option>
                <option value="PROBATION">PROBATION</option>
                <option value="SUSPENDED">SUSPENDED</option>
              </select>
            </label>
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Override reason</span>
              <textarea
                value={standingForm.standingOverrideReason}
                onChange={(event) =>
                  setStandingForm((current) => ({
                    ...current,
                    standingOverrideReason: event.target.value,
                  }))
                }
                rows={4}
                className="rounded-2xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-slate-900"
                required
              />
            </label>
            {message ? <p className="text-sm text-slate-700">{message}</p> : null}
            <button
              type="submit"
              className="min-h-11 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
            >
              Save standing
            </button>
          </form>
        </Panel>

        <Panel title="Financial flags" description="Create flags or clear existing ones directly from the student record.">
          <form
            className="mb-4 grid gap-4"
            onSubmit={(event) => {
              event.preventDefault()
              createFlagMutation.mutate({
                studentId,
                payload: flagForm,
              })
            }}
          >
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Flag type</span>
              <input
                value={flagForm.flagType}
                onChange={(event) => setFlagForm((current) => ({ ...current, flagType: event.target.value }))}
                className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
              />
            </label>
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Reason</span>
              <textarea
                value={flagForm.reason}
                onChange={(event) => setFlagForm((current) => ({ ...current, reason: event.target.value }))}
                rows={3}
                className="rounded-2xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-slate-900"
                required
              />
            </label>
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Effective date</span>
              <input
                type="date"
                value={flagForm.effectiveDate}
                onChange={(event) => setFlagForm((current) => ({ ...current, effectiveDate: event.target.value }))}
                className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
                required
              />
            </label>
            <button
              type="submit"
              className="min-h-11 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
            >
              Create flag
            </button>
          </form>

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
                  <button
                    type="button"
                    onClick={() =>
                      clearFlagMutation.mutate({
                        studentId,
                        flagId: flag.id,
                        payload: { clearedDate: new Date().toISOString().slice(0, 10) },
                      })
                    }
                    className="mt-3 min-h-11 rounded-2xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700"
                  >
                    Clear flag
                  </button>
                </article>
              ))}
            </div>
          ) : (
            <DataState title="No flags" message="No financial flags are active." />
          )}
        </Panel>

        <Panel title="Advising note approvals" description="Draft notes become visible to students only after admin approval.">
          {notesQuery.isLoading ? (
            <DataState title="Loading notes" message="Fetching advising notes." />
          ) : notesQuery.isError ? (
            <DataState title="Note load failed" message="Advising notes could not be loaded." />
          ) : notesQuery.data && notesQuery.data.length ? (
            <div className="space-y-3">
              {notesQuery.data.map((note) => (
                <article key={note.id} className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                  <p className="text-sm font-semibold text-slate-900">{note.status}</p>
                  <p className="mt-2 text-sm text-slate-600">{note.note_text}</p>
                  {note.status !== 'APPROVED' ? (
                    <button
                      type="button"
                      onClick={() => approveNoteMutation.mutate({ studentId, noteId: note.id })}
                      className="mt-3 min-h-11 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                    >
                      Approve note
                    </button>
                  ) : null}
                </article>
              ))}
            </div>
          ) : (
            <DataState title="No notes" message="No advising notes exist for this student yet." />
          )}
        </Panel>

        <Panel title="Correction request review" description="Review student correction requests directly from the record.">
          {correctionsQuery.isLoading ? (
            <DataState title="Loading corrections" message="Fetching correction requests." />
          ) : correctionsQuery.isError ? (
            <DataState title="Correction load failed" message="Correction requests could not be loaded." />
          ) : correctionsQuery.data && correctionsQuery.data.length ? (
            <div className="space-y-3">
              {correctionsQuery.data.map((request) => (
                <article key={request.id} className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                  <p className="text-sm font-semibold text-slate-900">{request.status}</p>
                  <p className="mt-2 text-sm text-slate-600">{request.requested_changes}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        reviewCorrectionMutation.mutate({
                          studentId,
                          correctionRequestId: request.id,
                          payload: {
                            status: 'APPROVED',
                            reviewNote: 'Approved by admin in Step 2.4 frontend.',
                          },
                        })
                      }
                      className="min-h-11 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                    >
                      Approve
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        reviewCorrectionMutation.mutate({
                          studentId,
                          correctionRequestId: request.id,
                          payload: {
                            status: 'REJECTED',
                            reviewNote: 'Rejected by admin in Step 2.4 frontend.',
                          },
                        })
                      }
                      className="min-h-11 rounded-2xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700"
                    >
                      Reject
                    </button>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <DataState title="No corrections" message="No correction requests have been filed." />
          )}
        </Panel>

        <Panel title="Grade release" description="Admins can update draft scores and officialise grades from the student record.">
          {gradesQuery.isLoading ? (
            <DataState title="Loading grades" message="Fetching grades." />
          ) : gradesQuery.isError ? (
            <DataState title="Grade load failed" message="Grades could not be loaded." />
          ) : gradesQuery.data && gradesQuery.data.length ? (
            <div className="space-y-3">
              {gradesQuery.data.map((grade) => (
                <article key={grade.id} className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-900">{grade.course_code}</p>
                      <p className="mt-1 text-sm text-slate-600">
                        {grade.numeric_score ?? grade.special_code} · {grade.grade_status}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {grade.grade_status !== 'OFFICIAL' ? (
                        <button
                          type="button"
                          onClick={() => officialiseMutation.mutate(grade.id)}
                          className="min-h-11 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                        >
                          Officialise
                        </button>
                      ) : null}
                      <button
                        type="button"
                        onClick={() =>
                          gradeUpdateMutation.mutate({
                            gradeId: grade.id,
                            payload: {
                              numericScore: grade.numeric_score ?? undefined,
                              specialCode: grade.special_code || undefined,
                              changeReason: 'Updated by admin from Step 2.4 frontend.',
                            },
                          })
                        }
                        className="min-h-11 rounded-2xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700"
                      >
                        Re-save
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <DataState title="No grades" message="No grades have been recorded yet." />
          )}
        </Panel>
      </div>
    </div>
  )
}
