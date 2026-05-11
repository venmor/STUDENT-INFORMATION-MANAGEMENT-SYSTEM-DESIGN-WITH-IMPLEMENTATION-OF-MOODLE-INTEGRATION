import { useMutation } from '@tanstack/react-query'

import { api } from '@/api/axios'

interface SummariseInput {
  raw_text: string
  student_id?: string | null
}

interface SummarisationOutput {
  id: string
  raw_input_text: string
  ai_output: {
    key_issues: string[]
    recommended_actions: string[]
    urgency_level: 'Routine' | 'Follow-up Needed' | 'Urgent'
  }
  human_edited_output: {
    key_issues: string[]
    recommended_actions: string[]
    urgency_level: string
  } | null
  status: 'PENDING' | 'APPROVED' | 'DISCARDED'
  provider: string
  model_name: string
  latency_ms: number | null
  student: string | null
  advising_note: string | null
  created_at: string
  approved_at: string | null
}

interface ApproveInput {
  key_issues: string[]
  recommended_actions: string[]
  urgency_level: string
}

export function useSummariseMutation() {
  return useMutation({
    mutationFn: async (input: SummariseInput): Promise<SummarisationOutput> => {
      const response = await api.post('/ai/summarise/', input)
      return response.data
    },
  })
}

export function useApproveSummarisationMutation(summarisationId: string) {
  return useMutation({
    mutationFn: async (input: ApproveInput): Promise<SummarisationOutput> => {
      const response = await api.post(`/ai/summarise/${summarisationId}/approve/`, input)
      return response.data
    },
  })
}
