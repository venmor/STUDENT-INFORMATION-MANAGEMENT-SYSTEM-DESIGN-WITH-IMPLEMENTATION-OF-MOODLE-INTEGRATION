import { useState } from 'react'

import { Button } from '@/components/ui/Button'
import { MoodSelector } from '@/components/wellbeing/MoodSelector'
import { Textarea } from '@/components/ui/Textarea'

export function WellbeingCheckInForm() {
  const [mood, setMood] = useState<number | undefined>()

  return (
    <div className="space-y-5 rounded-2xl border border-wellbeing-muted bg-white p-6">
      <div>
        <h3 className="text-2xl font-semibold text-neutral-900">How are you feeling today?</h3>
        <p className="mt-1 text-sm text-neutral-500">
          This response is private and only visible to designated wellbeing staff.
        </p>
      </div>
      <MoodSelector value={mood} onChange={setMood} />
      <Textarea
        id="wellbeing-note"
        label="Anything you&apos;d like to share? (optional)"
        rows={4}
        placeholder="You don&apos;t have to write anything. This space is here if you want it."
      />
      <Button disabled={!mood} className="w-full bg-wellbeing-accent hover:bg-violet-800">
        Submit check-in
      </Button>
    </div>
  )
}
