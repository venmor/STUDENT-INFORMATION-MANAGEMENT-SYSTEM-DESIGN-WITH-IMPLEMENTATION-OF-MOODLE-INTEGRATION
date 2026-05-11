import { PencilSquareIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { EmptyState } from '@/components/ui/EmptyState'
import { Textarea } from '@/components/ui/Textarea'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import { useStudentMutations, useCorrectionRequests } from '@/hooks/useStudents'
import { useState } from 'react'

export function StudentCorrectionsPage() {
  const user = useCurrentUser()
  const requests = useCorrectionRequests(user?.studentProfileId ?? undefined)
  const mutations = useStudentMutations(user?.studentProfileId ?? undefined)
  const [requestedChanges, setRequestedChanges] = useState('')
  const [justification, setJustification] = useState('')

  return (
    <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
      <Card>
        <CardTitle>Submit a correction request</CardTitle>
        <div className="mt-4 space-y-5">
          <Input
            id="requested-changes"
            label="Requested changes"
            placeholder="Example: Update programme or correct student number"
            value={requestedChanges}
            onChange={(event) => setRequestedChanges(event.target.value)}
          />
          <Textarea
            id="justification"
            label="Justification"
            placeholder="Explain why the record should be corrected."
            value={justification}
            onChange={(event) => setJustification(event.target.value)}
          />
          <Button
            loading={mutations.createCorrectionRequest.isPending}
            onClick={() =>
              mutations.createCorrectionRequest.mutate({
                requestedChanges,
                justification,
              })
            }
          >
            Submit request
          </Button>
        </div>
      </Card>
      <Card>
        <CardTitle>Request history</CardTitle>
        <div className="mt-4 space-y-3">
          {requests.data?.length ? (
            requests.data.map((request) => (
              <div key={request.id} className="rounded-xl border border-neutral-200 px-4 py-3">
                <p className="font-medium text-neutral-900">{request.requested_changes}</p>
                <p className="mt-1 text-sm text-neutral-600">{request.justification}</p>
                <p className="mt-2 font-mono text-xs uppercase tracking-wide text-neutral-500">
                  {request.status}
                </p>
              </div>
            ))
          ) : (
            <EmptyState
              icon={<PencilSquareIcon className="h-12 w-12" />}
              title="No correction requests"
              description="Submitted correction requests will appear here with their current review status."
            />
          )}
        </div>
      </Card>
    </div>
  )
}
