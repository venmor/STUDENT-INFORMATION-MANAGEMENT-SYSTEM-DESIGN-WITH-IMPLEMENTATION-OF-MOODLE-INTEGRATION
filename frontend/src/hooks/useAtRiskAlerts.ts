import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from '@/api/axios'

export interface AtRiskAlert {
  id: string
  student: string
  student_name: string
  student_number: string
  severity: 'HIGH' | 'MEDIUM' | 'LOW'
  active_signals: string[]
  explanation: string
  provider: string
  model_name: string
  is_acknowledged: boolean
  acknowledged_by: string | null
  acknowledged_at: string | null
  is_closed: boolean
  closed_at: string | null
  created_at: string
  updated_at: string
}

export function useAtRiskAlerts() {
  return useQuery<AtRiskAlert[]>({
    queryKey: ['at-risk-alerts'],
    queryFn: async () => {
      const response = await api.get('/advisor/at-risk/alerts')
      return response.data
    },
  })
}

export function useAtRiskAlertHistory() {
  return useQuery<AtRiskAlert[]>({
    queryKey: ['at-risk-alerts-history'],
    queryFn: async () => {
      const response = await api.get('/advisor/at-risk/history')
      return response.data
    },
  })
}

export function useAcknowledgeAlertMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (alertId: string): Promise<AtRiskAlert> => {
      const response = await api.post(`/advisor/at-risk/alerts/${alertId}/acknowledge`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['at-risk-alerts'] })
      queryClient.invalidateQueries({ queryKey: ['at-risk-alerts-history'] })
    },
  })
}
