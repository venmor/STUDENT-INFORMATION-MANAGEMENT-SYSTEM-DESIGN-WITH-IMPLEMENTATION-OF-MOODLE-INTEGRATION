import { useState } from 'react'
import { SparklesIcon, XMarkIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'
import { CopilotDisclaimer } from '@/components/ai/CopilotDisclaimer'
import { CopilotMessageBubble } from '@/components/ai/CopilotMessageBubble'
import { Skeleton } from '@/components/ui/Skeleton'

export function CopilotDrawer() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <button
        type="button"
        aria-label="Ask Co-pilot"
        className="fixed bottom-6 right-6 z-30 flex h-14 w-14 items-center justify-center rounded-full bg-primary text-white shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2"
        onClick={() => setOpen(true)}
      >
        <SparklesIcon className="h-6 w-6" />
      </button>
      {open ? (
        <aside className="fixed inset-y-0 right-0 z-40 flex h-screen w-full max-w-md flex-col border-l border-neutral-200 bg-white shadow-modal">
          <div className="flex items-center justify-between border-b border-neutral-200 px-4 py-4">
            <div>
              <p className="font-display text-lg font-bold text-neutral-900">Student Co-pilot</p>
              <p className="text-sm text-neutral-500">Deferred until the AI backend phase</p>
            </div>
            <Button variant="ghost" size="sm" className="min-w-0 px-2" onClick={() => setOpen(false)}>
              <XMarkIcon className="h-5 w-5" />
            </Button>
          </div>
          <CopilotDisclaimer />
          <div className="flex-1 space-y-4 overflow-y-auto p-4">
            <CopilotMessageBubble role="user">When does course registration close?</CopilotMessageBubble>
            <div className="max-w-[80%] rounded-2xl rounded-bl-sm bg-neutral-100 px-4 py-3" aria-label="Copilot loading">
              <Skeleton className="h-4 w-40" />
              <Skeleton className="mt-2 h-4 w-28" />
            </div>
            <CopilotMessageBubble
              role="assistant"
              source="Deferred until Phase 4 AI build"
              confidenceNote="I&apos;m not certain about this. Please verify with the Registrar."
            >
              The live co-pilot service is not available in the current Step 2.4 backend contract.
            </CopilotMessageBubble>
          </div>
          <div className="border-t border-neutral-200 p-4">
            <textarea
              className="h-24 w-full rounded-xl border border-neutral-300 bg-neutral-50 px-4 py-3 text-sm text-neutral-500"
              disabled
              value="The co-pilot input is disabled until the AI service endpoints are implemented."
              readOnly
            />
          </div>
        </aside>
      ) : null}
    </>
  )
}
