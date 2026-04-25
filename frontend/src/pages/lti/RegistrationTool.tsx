import { DeferredFeaturePanel } from '@/components/ui/DeferredFeaturePanel'

export function RegistrationToolPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <DeferredFeaturePanel phaseLabel="Phase 3" title="LTI registration tool">
        The embedded registration experience depends on the LTI provider and Moodle launch flow in the later
        integration phase.
      </DeferredFeaturePanel>
    </div>
  )
}
