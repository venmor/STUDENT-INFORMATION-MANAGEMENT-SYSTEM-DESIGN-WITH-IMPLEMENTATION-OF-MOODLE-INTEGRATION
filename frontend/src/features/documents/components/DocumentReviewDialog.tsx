import { useState } from 'react'

import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { Textarea } from '@/components/ui/Textarea'
import type { StudentDocument } from '@/types/documents'

export function DocumentReviewDialog({
  action,
  document,
  isPending = false,
  onOpenChange,
  onSubmit,
  open,
}: {
  action: 'approve' | 'reject'
  document?: StudentDocument | null
  isPending?: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (reviewNote: string) => void
  open: boolean
}) {
  const [reviewNote, setReviewNote] = useState('')
  const title = action === 'approve' ? 'Approve Document' : 'Reject Document'
  const buttonLabel = action === 'approve' ? 'Approve document' : 'Reject document'

  return (
    <Modal
      open={open}
      onOpenChange={(nextOpen) => {
        onOpenChange(nextOpen)
        if (!nextOpen) {
          setReviewNote('')
        }
      }}
      title={title}
      description={document ? `${document.title} for ${document.student.fullName}` : undefined}
    >
      <div className="space-y-4">
        <Textarea
          id="document-review-note"
          label="Review note"
          rows={4}
          value={reviewNote}
          onChange={(event) => setReviewNote(event.target.value)}
          hint={action === 'reject' ? 'Explain what the student or admin should correct.' : 'Optional note for the review record.'}
        />
        <div className="flex flex-wrap justify-end gap-3">
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            variant={action === 'reject' ? 'destructive' : 'primary'}
            loading={isPending}
            onClick={() => onSubmit(reviewNote)}
          >
            {buttonLabel}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
