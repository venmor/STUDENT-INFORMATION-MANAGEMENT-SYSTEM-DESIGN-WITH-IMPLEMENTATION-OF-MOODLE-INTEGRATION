import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  getNotifications,
  getNotificationSummary,
  markAllNotificationsRead,
  markNotificationRead,
} from '@/api/notifications'
import type { NotificationFilters } from '@/types/notifications'

export function useNotificationSummary() {
  return useQuery({
    queryKey: ['notifications', 'summary'],
    queryFn: getNotificationSummary,
  })
}

export function useNotifications(filters: NotificationFilters = {}) {
  return useQuery({
    queryKey: ['notifications', 'list', filters],
    queryFn: () => getNotifications(filters),
  })
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}
