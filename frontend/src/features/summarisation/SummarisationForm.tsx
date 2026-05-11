import { useState } from 'react'

import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Textarea'

const MAX_INPUT_LENGTH = 5000
const GOVERNANCE_NOTICE =
  'AI-generated summaries must be reviewed and approved before saving. The saved record will reflect your approved version, not the raw AI output.'

export function SummarisationForm({
  onSubmit,
  isPending,
}: {
  onSubmit: (rawText: string) => void
  isPending: boolean
}) {
  const [text, setText] = useState('')
  const charCount = text.length
  const isOverLimit = charCount > MAX_INPUT_LENGTH
  const isEmpty = text.trim().length === 0

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        {GOVERNANCE_NOTICE}
      </div>
      <div>
        <Textarea
          id="summarise-input"
          label="Raw advising notes"
          rows={8}
          placeholder="Paste or type your advising notes, meeting minutes, or helpdesk ticket here."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={isPending}
        />
        <div className="mt-1 flex justify-end">
          <span
            className={`text-xs ${isOverLimit ? 'font-medium text-red-600' : 'text-neutral-500'}`}
          >
            {charCount} / {MAX_INPUT_LENGTH}
          </span>
        </div>
        {isOverLimit && (
          <p className="mt-1 text-sm text-red-600">
            Input exceeds the {MAX_INPUT_LENGTH} character limit. Please shorten your text.
          </p>
        )}
      </div>
      <Button
        onClick={() => onSubmit(text)}
        loading={isPending}
        disabled={isEmpty || isOverLimit || isPending}
      >
        Generate summary
      </Button>
    </div>
  )
}
