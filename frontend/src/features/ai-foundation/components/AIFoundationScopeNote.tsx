import { ShieldCheckIcon } from '@heroicons/react/24/outline'

import { Alert } from '@/components/ui/Alert'

export function AIFoundationScopeNote() {
  return (
    <Alert tone="info" icon={<ShieldCheckIcon className="h-5 w-5" />} title="Current Scope">
      <p>This page tests retrieval only. It does not call an LLM or generate student-facing AI answers.</p>
      <p className="mt-2">Step 4.2 will build the student service co-pilot on top of this foundation.</p>
      <p className="mt-2">
        Knowledge sources are institutional policy or demo text only. Private student documents are not embedded into the vector store.
      </p>
    </Alert>
  )
}
