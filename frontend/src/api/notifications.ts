import { api } from '@/api/axios'
import type {
  MarkAllNotificationsReadResponse,
  NotificationFilters,
  NotificationItem,
  NotificationSummary,
} from '@/types/notifications'

function filterParam(value?: string) {
  return value && value !== 'ALL' ? value : undefined
}

export async function getNotifications(filters: NotificationFilters = {}) {
  const response = await api.get<NotificationItem[]>('/notifications', {
    params: {
      status: filters.status && filters.status !== 'ALL' ? filters.status.toLowerCase() : undefined,
      category: filterParam(filters.category),
      severity: filterParam(filters.severity),
    },
  })
  return response.data
}

export async function getNotificationSummary() {
  const response = await api.get<NotificationSummary>('/notifications/summary')
  return response.data
}

export async function markNotificationRead(notificationId: string) {
  const response = await api.post<NotificationItem>(`/notifications/${notificationId}/read`)
  return response.data
}

export async function markAllNotificationsRead() {
  const response = await api.post<MarkAllNotificationsReadResponse>('/notifications/read-all')
  return response.data
}
