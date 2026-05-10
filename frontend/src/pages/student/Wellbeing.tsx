import { DeferredFeaturePanel } from '@/components/ui/DeferredFeaturePanel'
import { QuickExitButton } from '@/components/wellbeing/QuickExitButton'
import { WellbeingCheckInForm } from '@/components/wellbeing/WellbeingCheckInForm'
import { WellbeingConsentPage } from '@/components/wellbeing/WellbeingConsentPage'
import { WellbeingEscalationScreen } from '@/components/wellbeing/WellbeingEscalationScreen'

export function StudentWellbeingPage() {
  return (
    <div className="min-h-[70vh] rounded-2xl bg-wellbeing-soft px-4 py-8">
      <div className="relative mx-auto max-w-4xl space-y-6 pt-12">
        <QuickExitButton />
        <DeferredFeaturePanel phaseLabel="Phase 6" title="Wellbeing support is approval-gated">
          The wellbeing workflow is documented and designed here, but its safeguarded backend, restricted schema,
          and staffing approvals belong to the later wellbeing phase rather than Step 2.4.
        </DeferredFeaturePanel>
        <WellbeingConsentPage />
        <WellbeingCheckInForm />
        <WellbeingEscalationScreen />
      </div>
    </div>
  )
}
