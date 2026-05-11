import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { getCopilotSessions, queryCopilot } from '@/api/copilot'
import type { CopilotChatMessage, CopilotQueryResponse, CopilotSource } from '@/types/copilot'

const nowIso = () => new Date().toISOString()

function userMessage(question: string): CopilotChatMessage {
  return {
    id: `user-${Date.now()}`,
    role: 'USER',
    content: question,
    createdAt: nowIso(),
  }
}

function assistantMessage(response: CopilotQueryResponse): CopilotChatMessage {
  return {
    id: response.messageId,
    role: 'ASSISTANT',
    content: response.answer,
    createdAt: nowIso(),
    confidence: response.confidence,
    sources: response.sources,
    suggestedNextActions: response.suggestedNextActions,
    disclaimer: response.disclaimer,
  }
}

export function useCopilot() {
  const queryClient = useQueryClient()
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<CopilotChatMessage[]>([])
  const [error, setError] = useState<string | null>(null)
  const [lastQuestion, setLastQuestion] = useState('')
  const [thinkingLabel, setThinkingLabel] = useState('Searching institutional sources...')

  const sessionsQuery = useQuery({
    queryKey: ['copilot', 'sessions'],
    queryFn: getCopilotSessions,
  })

  const queryMutation = useMutation({
    mutationFn: queryCopilot,
    onMutate: () => {
      setError(null)
      setThinkingLabel('Searching institutional sources...')
    },
    onSuccess: (response) => {
      setActiveSessionId(response.sessionId)
      setMessages((current) => [...current, assistantMessage(response)])
      queryClient.invalidateQueries({ queryKey: ['copilot', 'sessions'] })
    },
    onError: () => {
      setError('The co-pilot could not answer that question.')
    },
  })

  function submitQuestion(question: string) {
    const cleaned = question.trim()
    if (!cleaned || queryMutation.isPending) {
      return
    }
    setLastQuestion(cleaned)
    setMessages((current) => [...current, userMessage(cleaned)])
    queryMutation.mutate({ question: cleaned, sessionId: activeSessionId })
    window.setTimeout(() => {
      setThinkingLabel('Preparing answer...')
    }, 250)
  }

  function retryLastQuestion() {
    if (lastQuestion) {
      submitQuestion(lastQuestion)
    }
  }

  function startNewSession() {
    setActiveSessionId(null)
    setMessages([])
    setError(null)
  }

  const currentSources = useMemo<CopilotSource[]>(() => {
    const lastAssistant = [...messages].reverse().find((message) => message.role === 'ASSISTANT')
    return lastAssistant?.sources ?? []
  }, [messages])

  return {
    activeSessionId,
    currentSources,
    error,
    isLoadingSessions: sessionsQuery.isLoading,
    isThinking: queryMutation.isPending,
    messages,
    retryLastQuestion,
    sessions: sessionsQuery.data ?? [],
    startNewSession,
    submitQuestion,
    thinkingLabel,
  }
}
