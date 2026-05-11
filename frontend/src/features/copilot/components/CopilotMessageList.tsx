import { CopilotEmptyState } from '@/features/copilot/components/CopilotEmptyState'
import { CopilotMessageBubble } from '@/features/copilot/components/CopilotMessageBubble'
import { CopilotThinkingIndicator } from '@/features/copilot/components/CopilotThinkingIndicator'
import type { CopilotChatMessage } from '@/types/copilot'

export function CopilotMessageList({
  messages,
  thinkingLabel,
  isThinking,
  onSelectPrompt,
}: {
  messages: CopilotChatMessage[]
  thinkingLabel: string
  isThinking: boolean
  onSelectPrompt: (prompt: string) => void
}) {
  return (
    <section
      aria-label="AI co-pilot conversation"
      className="min-h-[26rem] flex-1 space-y-4 overflow-y-auto rounded-lg border border-neutral-200 bg-neutral-50 p-4"
    >
      {messages.length === 0 ? <CopilotEmptyState onSelectPrompt={onSelectPrompt} /> : null}
      {messages.map((message) => (
        <CopilotMessageBubble key={message.id} message={message} />
      ))}
      {isThinking ? <CopilotThinkingIndicator label={thinkingLabel} /> : null}
    </section>
  )
}
