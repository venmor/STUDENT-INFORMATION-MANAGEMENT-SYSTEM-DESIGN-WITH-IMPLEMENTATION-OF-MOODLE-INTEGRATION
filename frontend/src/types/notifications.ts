export type NotificationCategory = 'ACADEMIC' | 'MOODLE' | 'GRADES' | 'ENROLLMENT' | 'ADVISING' | 'SYSTEM'

export type NotificationSeverity = 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR'

export type NotificationStatusFilter = 'ALL' | 'UNREAD' | 'READ'

export interface NotificationItem {
  id: string
  category: NotificationCategory
  severity: NotificationSeverity
  title: string
  message: string
  actionLabel: string
  actionUrl: string
  isRead: boolean
  readAt: string | null
  createdAt: string
  sourceType: string
  sourceId: string
}

export interface NotificationSummary {
  unreadCount: number
  latest: NotificationItem[]
  byCategory: Record<NotificationCategory, number>
}

export interface NotificationFilters {
  status?: NotificationStatusFilter
  category?: NotificationCategory | 'ALL'
  severity?: NotificationSeverity | 'ALL'
}

export interface MarkAllNotificationsReadResponse {
  updatedCount: number
}
