import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { wellbeingApi } from '@/api/wellbeing'

export function useWellbeingConsent() {
  return useQuery({
    queryKey: ['wellbeing', 'consent'],
    queryFn: wellbeingApi.getConsent,
  })
}

export function useUpdateWellbeingConsent() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: wellbeingApi.updateConsent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wellbeing'] })
    },
  })
}

export function useWellbeingTriage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: wellbeingApi.submitTriage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wellbeing', 'history'] })
    },
  })
}

export function useWellbeingHistory() {
  return useQuery({
    queryKey: ['wellbeing', 'history'],
    queryFn: wellbeingApi.getHistory,
  })
}

export function useDeleteWellbeingCheckIn() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: wellbeingApi.deleteCheckIn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['wellbeing', 'history'] })
    },
  })
}

export function useWellbeingCoordinatorAlerts() {
  return useQuery({
    queryKey: ['wellbeing', 'coordinator', 'alerts'],
    queryFn: wellbeingApi.getCoordinatorAlerts,
    refetchInterval: 30000, // Check every 30s
  })
}
