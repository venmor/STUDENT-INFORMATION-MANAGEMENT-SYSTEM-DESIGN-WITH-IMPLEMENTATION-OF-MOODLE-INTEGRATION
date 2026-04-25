import { DeferredFeaturePanel } from '@/components/ui/DeferredFeaturePanel'
import { AtRiskAlertRow } from '@/components/advisor/AtRiskAlertRow'

export function AtRiskAlertQueue() {
  return (
    <div className="space-y-4">
      <AtRiskAlertRow
        severity="HIGH"
        studentName="Deferred until AI phase"
        timestamp="Phase 4"
        explanation="The at-risk engine is defined in the SRS but is not implemented in the current Step 2.4 backend contract."
      />
      <DeferredFeaturePanel phaseLabel="Phase 4" title="At-risk processing">
        The nightly at-risk engine, advisor acknowledgement workflow, and alert history remain later-phase AI
        features. This queue preserves the intended advisor-first layout without faking operational alerts.
      </DeferredFeaturePanel>
    </div>
  )
}
