import { CopilotComposer } from '@/features/copilot/components/CopilotComposer'
import { CopilotErrorState } from '@/features/copilot/components/CopilotErrorState'
import { CopilotMessageList } from '@/features/copilot/components/CopilotMessageList'
import { CopilotSafetyNotice } from '@/features/copilot/components/CopilotSafetyNotice'
import { CopilotSessionList } from '@/features/copilot/components/CopilotSessionList'
import { CopilotSourcePanel } from '@/features/copilot/components/CopilotSourcePanel'
import { useCopilot } from '@/hooks/useCopilot'

export function CopilotChatShell() {
  const copilot = useCopilot()

  return (
    <div className="grid gap-4 xl:grid-cols-[16rem_minmax(0,1fr)_20rem]">
      <div className="space-y-4 xl:order-1">
        <CopilotSessionList
          activeSessionId={copilot.activeSessionId}
          isLoading={copilot.isLoadingSessions}
          onNewChat={copilot.startNewSession}
          sessions={copilot.sessions}
        />
      </div>
      <div className="flex min-h-[42rem] flex-col gap-4 xl:order-2">
        <CopilotSafetyNotice />
        <CopilotMessageList
          messages={copilot.messages}
          isThinking={copilot.isThinking}
          thinkingLabel={copilot.thinkingLabel}
          onSelectPrompt={copilot.submitQuestion}
        />
        {copilot.error ? <CopilotErrorState message={copilot.error} onRetry={copilot.retryLastQuestion} /> : null}
        <CopilotComposer disabled={copilot.isThinking} onSubmit={copilot.submitQuestion} />
      </div>
      <div className="xl:order-3">
        <CopilotSourcePanel sources={copilot.currentSources} />
      </div>
    </div>
  )
}
