export type CopilotConfidence = 'HIGH' | 'MEDIUM' | 'LOW' | 'UNSUPPORTED'
export type CopilotMessageRole = 'USER' | 'ASSISTANT' | 'SYSTEM'
export type CopilotSessionStatus = 'ACTIVE' | 'ARCHIVED'

export interface CopilotSource {
  sourceId: string
  chunkId: string
  title: string
  sourceType: string
  preview: string
  score: number
}

export interface CopilotSuggestedAction {
  label: string
  url: string
}

export interface CopilotQueryRequest {
  question: string
  sessionId?: string | null
}

export interface CopilotQueryResponse {
  sessionId: string
  messageId: string
  answer: string
  confidence: CopilotConfidence
  sources: CopilotSource[]
  suggestedNextActions: CopilotSuggestedAction[]
  disclaimer: string
}

export interface CopilotSession {
  id: string
  studentId: string | null
  title: string
  status: CopilotSessionStatus
  metadata: Record<string, unknown>
  createdAt: string
  updatedAt: string
  lastMessageAt: string | null
}

export interface CopilotMessage {
  id: string
  role: CopilotMessageRole
  content: string
  sourceReferences: CopilotSource[]
  confidence: CopilotConfidence
  provider: string
  modelName: string
  retrievedChunkCount: number
  latencyMs: number | null
  metadata: Record<string, unknown>
  createdAt: string
}

export interface CopilotSessionDetail extends CopilotSession {
  messages: CopilotMessage[]
}

export interface CopilotChatMessage {
  id: string
  role: CopilotMessageRole
  content: string
  createdAt: string
  confidence?: CopilotConfidence
  sources?: CopilotSource[]
  suggestedNextActions?: CopilotSuggestedAction[]
  disclaimer?: string
  pending?: boolean
}

export interface CopilotFeedbackRequest {
  rating: 'HELPFUL' | 'NOT_HELPFUL'
  comment?: string
}
