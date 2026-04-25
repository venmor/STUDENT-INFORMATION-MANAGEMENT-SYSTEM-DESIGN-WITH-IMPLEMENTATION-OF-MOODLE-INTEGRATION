import { DeferredFeaturePanel } from '@/components/ui/DeferredFeaturePanel'

export function AdvisingToolPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <DeferredFeaturePanel phaseLabel="Phase 3" title="LTI advising tool">
        LTI launch, Moodle context validation, and embedded advising tools are part of the Moodle integration phase.
      </DeferredFeaturePanel>
    </div>
  )
}
