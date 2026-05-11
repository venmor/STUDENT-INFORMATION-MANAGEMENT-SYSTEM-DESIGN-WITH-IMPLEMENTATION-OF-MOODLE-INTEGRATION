import { Button } from '@/components/ui/Button'

export function WellbeingConsentPage() {
  return (
    <div className="rounded-2xl border border-wellbeing-muted bg-white p-6">
      <h3 className="font-display text-2xl font-bold text-wellbeing-accent">Wellbeing Check-In</h3>
      <p className="mt-3 text-sm text-neutral-600">
        This safeguarded workflow is governed by later-phase approvals and backend support. The final consent content
        and restricted data flow are defined in the SRS and setup guide.
      </p>
      <div className="mt-5 flex flex-wrap gap-3">
        <Button className="bg-wellbeing-accent hover:bg-violet-800">Enable Wellbeing Check-In</Button>
        <Button variant="ghost">Return to dashboard</Button>
      </div>
    </div>
  )
}
