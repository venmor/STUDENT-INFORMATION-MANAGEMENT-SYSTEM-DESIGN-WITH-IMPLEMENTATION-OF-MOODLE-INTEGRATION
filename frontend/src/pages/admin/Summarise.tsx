import { useState } from 'react'

import { Card, CardTitle } from '@/components/ui/Card'
import { SummarisationForm } from '@/features/summarisation/SummarisationForm'
import { SummarisationResult } from '@/features/summarisation/SummarisationResult'
import { useApproveSummarisationMutation, useSummariseMutation } from '@/hooks/useSummarisation'

export function AdminSummarisePage() {
  const summarise = useSummariseMutation()
  const [summarisationId, setSummarisationId] = useState<string | null>(null)
  const approve = useApproveSummarisationMutation(summarisationId ?? '')
  const [success, setSuccess] = useState(false)

  const handleSubmit = (rawText: string) => {
    setSuccess(false)
    summarise.mutate(
      { raw_text: rawText },
      { onSuccess: (data) => setSummarisationId(data.id) },
    )
  }

  const handleApprove = (output: {
    key_issues: string[]
    recommended_actions: string[]
    urgency_level: string
  }) => {
    approve.mutate(output, {
      onSuccess: () => {
        setSuccess(true)
        setSummarisationId(null)
        summarise.reset()
      },
    })
  }

  const handleDiscard = () => {
    setSummarisationId(null)
    summarise.reset()
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardTitle>AI note summarisation</CardTitle>
        <p className="mt-2 text-sm text-neutral-600">
          Paste advising notes, meeting minutes, or helpdesk tickets to generate a structured
          summary. Review and edit the result before saving.
        </p>
        <div className="mt-4">
          {success ? (
            <div className="space-y-4">
              <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
                Summary approved and saved.
              </div>
              <button
                type="button"
                className="text-sm text-primary hover:underline"
                onClick={() => setSuccess(false)}
              >
                Summarise another note
              </button>
            </div>
          ) : summarise.data && summarisationId ? (
            <SummarisationResult
              keyIssues={summarise.data.ai_output.key_issues}
              recommendedActions={summarise.data.ai_output.recommended_actions}
              urgencyLevel={summarise.data.ai_output.urgency_level}
              onApprove={handleApprove}
              onDiscard={handleDiscard}
              isApproving={approve.isPending}
            />
          ) : summarise.isError ? (
            <div className="space-y-4">
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
                Summarisation failed. Please try again.
              </div>
              <button
                type="button"
                className="text-sm text-primary hover:underline"
                onClick={() => summarise.reset()}
              >
                Try again
              </button>
            </div>
          ) : (
            <SummarisationForm onSubmit={handleSubmit} isPending={summarise.isPending} />
          )}
        </div>
      </Card>
    </div>
  )
}
