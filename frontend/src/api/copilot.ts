import { api } from '@/api/axios'
import type {
  CopilotFeedbackRequest,
  CopilotQueryRequest,
  CopilotQueryResponse,
  CopilotSession,
  CopilotSessionDetail,
} from '@/types/copilot'

export async function getCopilotSessions(): Promise<CopilotSession[]> {
  const response = await api.get<CopilotSession[]>('/ai/copilot/sessions')
  return response.data
}

export async function createCopilotSession(payload: { title?: string }): Promise<CopilotSession> {
  const response = await api.post<CopilotSession>('/ai/copilot/sessions', payload)
  return response.data
}

export async function getCopilotSession(sessionId: string): Promise<CopilotSessionDetail> {
  const response = await api.get<CopilotSessionDetail>(`/ai/copilot/sessions/${sessionId}`)
  return response.data
}

export async function archiveCopilotSession(sessionId: string): Promise<CopilotSession> {
  const response = await api.post<CopilotSession>(`/ai/copilot/sessions/${sessionId}/archive`)
  return response.data
}

export async function queryCopilot(payload: CopilotQueryRequest): Promise<CopilotQueryResponse> {
  const response = await api.post<CopilotQueryResponse>('/ai/copilot/query', payload)
  return response.data
}

export async function rateCopilotMessage(messageId: string, payload: CopilotFeedbackRequest) {
  const response = await api.post(`/ai/copilot/messages/${messageId}/feedback`, payload)
  return response.data
}
