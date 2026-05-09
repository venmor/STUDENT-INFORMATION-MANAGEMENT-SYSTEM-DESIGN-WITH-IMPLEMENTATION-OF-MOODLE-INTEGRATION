import { useState } from 'react'

import { SummarisationForm } from '@/features/summarisation/SummarisationForm'
import { SummarisationResult } from '@/features/summarisation/SummarisationResult'
import { useApproveSummarisationMutation, useSummariseMutation } from '@/hooks/useSummarisation'

export function AISummarisationPanel({ studentId }: { studentId?: string }) {
  const summarise = useSummariseMutation()
  const [summarisationId, setSummarisationId] = useState<string | null>(null)
  const approve = useApproveSummarisationMutation(summarisationId ?? '')
  const [success, setSuccess] = useState(false)

  const handleSubmit = (rawText: string) => {
    setSuccess(false)
    summarise.mutate(
      { raw_text: rawText, student_id: studentId ?? null },
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

  if (success) {
    return (
      <div className="space-y-4">
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
          Summary approved and saved as an official advising note.
        </div>
        <button
          type="button"
          className="text-sm text-primary hover:underline"
          onClick={() => setSuccess(false)}
        >
          Summarise another note
        </button>
      </div>
    )
  }

  if (summarise.data && summarisationId) {
    return (
      <SummarisationResult
        keyIssues={summarise.data.ai_output.key_issues}
        recommendedActions={summarise.data.ai_output.recommended_actions}
        urgencyLevel={summarise.data.ai_output.urgency_level}
        onApprove={handleApprove}
        onDiscard={handleDiscard}
        isApproving={approve.isPending}
      />
    )
  }

  if (summarise.isPending) {
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-3 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-300 border-t-blue-600" />
          <div>
            <p className="text-sm font-medium text-blue-800">AI is processing your notes...</p>
            <p className="text-xs text-blue-600">This may take up to 30 seconds. If the request fails, it will automatically retry up to 2 times.</p>
          </div>
        </div>
      </div>
    )
  }

  if (summarise.isError) {
    return (
      <div className="space-y-4">
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          Summarisation failed after multiple attempts. The AI service may be temporarily unavailable.
        </div>
        <button
          type="button"
          className="text-sm text-primary hover:underline"
          onClick={() => summarise.reset()}
        >
          Try again
        </button>
      </div>
    )
  }

  return <SummarisationForm onSubmit={handleSubmit} isPending={summarise.isPending} />
}
