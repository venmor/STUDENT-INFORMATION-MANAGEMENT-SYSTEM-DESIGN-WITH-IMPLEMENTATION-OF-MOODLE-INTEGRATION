import { Badge } from '@/components/ui/Badge'
import { CopilotSuggestedActions } from '@/features/copilot/components/CopilotSuggestedActions'
import type { CopilotChatMessage } from '@/types/copilot'
import { cn } from '@/utils/cn'

function formatTime(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return ''
  }
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function confidenceTone(confidence?: string) {
  if (confidence === 'HIGH') return 'success'
  if (confidence === 'MEDIUM') return 'info'
  if (confidence === 'LOW') return 'warning'
  return 'danger'
}

export function CopilotMessageBubble({ message }: { message: CopilotChatMessage }) {
  const assistant = message.role === 'ASSISTANT'

  return (
    <article className={cn('max-w-[88%] space-y-1', assistant ? 'mr-auto' : 'ml-auto text-right')} tabIndex={0}>
      <div
        className={cn(
          'rounded-lg px-4 py-3 text-sm leading-6 shadow-sm',
          assistant ? 'rounded-bl-sm border border-neutral-200 bg-white text-neutral-900' : 'rounded-br-sm bg-primary text-white',
        )}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {assistant ? (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <Badge tone={confidenceTone(message.confidence)}>Confidence: {message.confidence ?? 'UNSUPPORTED'}</Badge>
            {message.sources?.length ? <span className="text-xs text-neutral-500">{message.sources.length} source reference(s)</span> : null}
          </div>
        ) : null}
        {assistant && message.sources?.length ? (
          <div className="mt-3 space-y-1 border-t border-neutral-100 pt-3 text-xs text-neutral-600">
            {message.sources.slice(0, 2).map((source) => (
              <p key={source.chunkId}>
                Source: <span className="font-medium text-neutral-800">{source.title}</span>
              </p>
            ))}
          </div>
        ) : null}
        {assistant ? <CopilotSuggestedActions actions={message.suggestedNextActions ?? []} /> : null}
        {assistant && message.disclaimer ? <p className="mt-3 text-xs font-medium text-amber-800">{message.disclaimer}</p> : null}
      </div>
      <time className="block text-xs text-neutral-500">{formatTime(message.createdAt)}</time>
    </article>
  )
}
