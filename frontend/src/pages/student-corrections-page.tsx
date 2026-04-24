import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { createCorrectionRequest, getCorrectionRequests } from '@/api/students'
import { useAuth } from '@/auth/auth-context'
import { DataState } from '@/components/ui/data-state'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'
import { formatDateTime } from '@/utils/format'

export default function StudentCorrectionsPage() {
  const { session } = useAuth()
  const queryClient = useQueryClient()
  const studentId = session?.user.studentProfileId
  const [requestedChanges, setRequestedChanges] = useState('')
  const [justification, setJustification] = useState('')
  const [message, setMessage] = useState('')

  const correctionRequestsQuery = useQuery({
    queryKey: ['correction-requests', studentId],
    queryFn: () => getCorrectionRequests(studentId as string),
    enabled: Boolean(studentId),
  })

  const createMutation = useMutation({
    mutationFn: ({ studentId, payload }: { studentId: string; payload: { requestedChanges: string; justification: string } }) =>
      createCorrectionRequest(studentId, payload),
    onSuccess: async () => {
      setRequestedChanges('')
      setJustification('')
      setMessage('Correction request submitted.')
      await queryClient.invalidateQueries({ queryKey: ['correction-requests', studentId] })
    },
    onError: () => {
      setMessage('Correction request submission failed.')
    },
  })

  if (!studentId) {
    return (
      <DataState
        title="Student profile not linked"
        message="This account has no student profile identifier in the session payload yet."
      />
    )
  }

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Student corrections"
        title="Request record corrections"
        description="Students can submit correction requests for registrar review and track their current status."
      />

      <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel title="New request" description="Provide the exact correction needed and the supporting justification.">
          <form
            className="grid gap-4"
            onSubmit={(event) => {
              event.preventDefault()
              setMessage('')
              createMutation.mutate({
                studentId,
                payload: {
                  requestedChanges,
                  justification,
                },
              })
            }}
          >
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Requested changes</span>
              <textarea
                value={requestedChanges}
                onChange={(event) => setRequestedChanges(event.target.value)}
                rows={5}
                className="rounded-2xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-slate-900"
                required
              />
            </label>
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Justification</span>
              <textarea
                value={justification}
                onChange={(event) => setJustification(event.target.value)}
                rows={4}
                className="rounded-2xl border border-slate-300 bg-white px-4 py-3 outline-none transition focus:border-slate-900"
                required
              />
            </label>
            {message ? <p className="text-sm text-slate-700">{message}</p> : null}
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="min-h-12 rounded-2xl bg-slate-900 px-5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {createMutation.isPending ? 'Submitting...' : 'Submit correction request'}
            </button>
          </form>
        </Panel>

        <Panel title="Request history" description="Submitted requests remain visible with the latest review status.">
          {correctionRequestsQuery.isLoading ? (
            <DataState title="Loading correction requests" message="Fetching submitted requests." />
          ) : correctionRequestsQuery.isError ? (
            <DataState title="Request load failed" message="Correction request history could not be loaded." />
          ) : correctionRequestsQuery.data && correctionRequestsQuery.data.length ? (
            <div className="space-y-3">
              {correctionRequestsQuery.data.map((request) => (
                <article key={request.id} className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="text-sm font-semibold text-slate-900">{request.status}</p>
                    <p className="text-xs text-slate-500">Created {formatDateTime(request.created_at)}</p>
                  </div>
                  <p className="mt-3 text-sm text-slate-700">{request.requested_changes}</p>
                  <p className="mt-2 text-sm text-slate-500">{request.justification}</p>
                  {request.review_note ? (
                    <p className="mt-3 rounded-2xl bg-slate-100 px-3 py-2 text-sm text-slate-700">
                      Review note: {request.review_note}
                    </p>
                  ) : null}
                </article>
              ))}
            </div>
          ) : (
            <DataState title="No requests yet" message="No correction requests have been submitted." />
          )}
        </Panel>
      </div>
    </div>
  )
}
