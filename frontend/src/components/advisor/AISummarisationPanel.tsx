import { DeferredFeaturePanel } from '@/components/ui/DeferredFeaturePanel'
import { Textarea } from '@/components/ui/Textarea'
import { Button } from '@/components/ui/Button'

export function AISummarisationPanel() {
  return (
    <DeferredFeaturePanel phaseLabel="Phase 4" title="AI note summarisation">
      <div className="space-y-4">
        <p>
          The advisor summarisation workflow is specified in the SRS for the later AI phase. The live
          summarisation endpoint and audit trail are not available in Step 2.4.
        </p>
        <Textarea
          id="summarise-input"
          label="Raw advising notes"
          rows={6}
          placeholder="Paste or type notes here once the AI summarisation backend is implemented."
          disabled
        />
        <div className="flex gap-3">
          <Button disabled>Generate summary</Button>
          <Button variant="secondary" disabled>
            Approve &amp; save
          </Button>
        </div>
      </div>
    </DeferredFeaturePanel>
  )
}
