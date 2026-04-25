import type { ReactNode } from 'react'

import { cn } from '@/utils/cn'

export function CopilotMessageBubble({
  children,
  confidenceNote,
  role,
  source,
}: {
  children: ReactNode
  confidenceNote?: string
  role: 'assistant' | 'user'
  source?: string
}) {
  return (
    <div className={cn('max-w-[80%] space-y-1', role === 'user' ? 'ml-auto text-right' : 'mr-auto')}>
      <div
        className={cn(
          'rounded-2xl px-4 py-2.5 text-sm',
          role === 'user'
            ? 'rounded-br-sm bg-primary text-white'
            : 'rounded-bl-sm bg-neutral-100 text-neutral-900',
        )}
      >
        {children}
      </div>
      {source ? <p className="text-xs text-secondary">Source: {source}</p> : null}
      {confidenceNote ? <p className="text-xs text-warning">{confidenceNote}</p> : null}
    </div>
  )
}
