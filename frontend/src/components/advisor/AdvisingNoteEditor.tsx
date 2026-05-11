import { useState } from 'react'

import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Textarea'

export function AdvisingNoteEditor({
  initialValue = '',
  isPending,
  onApprove,
  onSave,
}: {
  initialValue?: string
  isPending?: boolean
  onApprove?: () => void
  onSave: (value: string) => void
}) {
  const [value, setValue] = useState(initialValue)

  return (
    <div className="space-y-4">
      <Textarea
        id="advising-note"
        label="Advising note"
        rows={6}
        placeholder="Record the meeting summary or intervention note."
        value={value}
        onChange={(event) => setValue(event.target.value)}
      />
      <div className="flex flex-wrap gap-3">
        <Button loading={isPending} onClick={() => onSave(value)}>
          Save draft
        </Button>
        {onApprove ? (
          <Button variant="secondary" onClick={onApprove}>
            Approve note
          </Button>
        ) : null}
      </div>
    </div>
  )
}
