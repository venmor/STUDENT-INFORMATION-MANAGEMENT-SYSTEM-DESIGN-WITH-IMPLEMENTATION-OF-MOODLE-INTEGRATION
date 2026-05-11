import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline'

import { CopilotExamplePrompts } from '@/features/copilot/components/CopilotExamplePrompts'

export function CopilotEmptyState({ onSelectPrompt }: { onSelectPrompt: (prompt: string) => void }) {
  return (
    <div className="rounded-lg border border-dashed border-neutral-300 bg-white p-6">
      <div className="flex items-start gap-4">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-primary-light text-primary">
          <ChatBubbleLeftRightIcon className="h-6 w-6" aria-hidden="true" />
        </div>
        <div className="min-w-0 flex-1">
          <h2 className="text-base font-semibold text-neutral-900">Ask a student service question</h2>
          <p className="mt-1 text-sm leading-6 text-neutral-600">
            Use the co-pilot for registration, deadlines, courses, grades, documents, and academic rules. It will cite
            sources when it has enough context.
          </p>
          <div className="mt-4">
            <CopilotExamplePrompts onSelect={onSelectPrompt} />
          </div>
        </div>
      </div>
    </div>
  )
}
