import { PlusIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'
import type { CopilotSession } from '@/types/copilot'

export function CopilotSessionList({
  activeSessionId,
  isLoading,
  onNewChat,
  sessions,
}: {
  activeSessionId: string | null
  isLoading: boolean
  onNewChat: () => void
  sessions: CopilotSession[]
}) {
  return (
    <aside aria-label="Recent co-pilot sessions" className="rounded-lg border border-neutral-200 bg-white p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-neutral-900">Recent Chats</h2>
          <p className="text-sm text-neutral-500">Your student co-pilot history.</p>
        </div>
        <Button variant="secondary" size="sm" className="min-w-0 px-3" onClick={onNewChat}>
          <PlusIcon className="h-4 w-4" aria-hidden="true" />
          New
        </Button>
      </div>
      <div className="mt-4 space-y-2">
        {isLoading ? <p className="text-sm text-neutral-500">Loading recent chats...</p> : null}
        {!isLoading && sessions.length === 0 ? <p className="text-sm text-neutral-500">No saved sessions yet.</p> : null}
        {sessions.slice(0, 8).map((session) => (
          <div
            key={session.id}
            className={
              session.id === activeSessionId
                ? 'rounded-lg border border-primary/30 bg-primary-light px-3 py-2 text-sm font-semibold text-primary'
                : 'rounded-lg border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm text-neutral-700'
            }
          >
            {session.title}
          </div>
        ))}
      </div>
    </aside>
  )
}
