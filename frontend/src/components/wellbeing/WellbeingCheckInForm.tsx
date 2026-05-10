import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { MoodSelector } from '@/features/wellbeing/MoodSelector'
import { useWellbeingConsent, useWellbeingTriage } from '@/hooks/useWellbeing'
import { Card } from '@/components/ui/Card'

export function WellbeingCheckInForm({ onComplete }: { onComplete?: (result: any) => void }) {
  const { data: consent } = useWellbeingConsent()
  const [rating, setRating] = useState<number | null>(null)
  const [comment, setComment] = useState('')
  const triageMutation = useWellbeingTriage()

  if (!consent?.is_enabled) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (rating === null) return

    triageMutation.mutate(
      { mood_rating: rating, comment },
      { onSuccess: (data) => onComplete?.(data) }
    )
  }

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-4">
            How are you feeling today?
          </label>
          <MoodSelector value={rating} onChange={setRating} />
        </div>

        <Input
          label="Any comments? (Optional)"
          placeholder="Tell us a bit more about how you're feeling..."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          maxLength={500}
        />

        <div className="flex justify-end">
          <Button
            type="submit"
            disabled={rating === null}
            loading={triageMutation.isPending}
            className="bg-wellbeing-accent hover:bg-violet-800 text-white"
          >
            Submit check-in
          </Button>
        </div>
      </form>
    </Card>
  )
}
