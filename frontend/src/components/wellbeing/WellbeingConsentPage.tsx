import { Button } from '@/components/ui/Button'
import { useUpdateWellbeingConsent, useWellbeingConsent } from '@/hooks/useWellbeing'

export function WellbeingConsentPage({ onEnabled }: { onEnabled?: () => void }) {
  const { data: consent, isLoading } = useWellbeingConsent()
  const enableMutation = useUpdateWellbeingConsent()

  if (isLoading) return <div className="animate-pulse h-32 bg-neutral-100 rounded-2xl" />

  if (consent?.is_enabled) return null

  return (
    <div className="rounded-2xl border border-wellbeing-muted bg-white p-6 shadow-sm">
      <h3 className="font-display text-2xl font-bold text-wellbeing-accent">Wellbeing Check-In</h3>
      <p className="mt-3 text-sm text-neutral-600 leading-relaxed">
        Your wellbeing matters. By enabling this feature, you can share how you're feeling and access
        support resources. Your data is restricted to designated wellbeing staff and can be deleted
        by you at any time.
      </p>
      <div className="mt-5 flex flex-wrap gap-3">
        <Button
          className="bg-wellbeing-accent hover:bg-violet-800 text-white"
          loading={enableMutation.isPending}
          onClick={() => enableMutation.mutate(true, { onSuccess: onEnabled })}
        >
          Enable Wellbeing Check-In
        </Button>
      </div>
    </div>
  )
}
