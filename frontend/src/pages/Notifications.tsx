import { type ReactNode, useState } from 'react'
import {
  BellIcon,
  CheckCircleIcon,
  ClipboardDocumentCheckIcon,
  Cog6ToothIcon,
  ExclamationTriangleIcon,
  IdentificationIcon,
  InformationCircleIcon,
  ServerStackIcon,
  ShieldCheckIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

import { Alert } from '@/components/ui/Alert'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Select } from '@/components/ui/Select'
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotificationSummary,
  useNotifications,
} from '@/hooks/useNotifications'
import type {
  NotificationCategory,
  NotificationFilters,
  NotificationItem,
  NotificationSeverity,
  NotificationStatusFilter,
} from '@/types/notifications'

type BadgeTone = 'default' | 'success' | 'warning' | 'danger' | 'info'
type Accent = 'danger' | 'warning' | 'success' | 'info'

const statusItems = [
  { label: 'All', value: 'ALL' },
  { label: 'Unread', value: 'UNREAD' },
  { label: 'Read', value: 'READ' },
]

const categoryItems = [
  { label: 'All', value: 'ALL' },
  { label: 'Academic', value: 'ACADEMIC' },
  { label: 'Moodle', value: 'MOODLE' },
  { label: 'Grades', value: 'GRADES' },
  { label: 'Enrollment', value: 'ENROLLMENT' },
  { label: 'Advising', value: 'ADVISING' },
  { label: 'System', value: 'SYSTEM' },
]

const severityItems = [
  { label: 'All', value: 'ALL' },
  { label: 'Info', value: 'INFO' },
  { label: 'Success', value: 'SUCCESS' },
  { label: 'Warning', value: 'WARNING' },
  { label: 'Error', value: 'ERROR' },
]

const categoryLabels: Record<NotificationCategory, string> = {
  ACADEMIC: 'Academic',
  MOODLE: 'Moodle',
  GRADES: 'Grades',
  ENROLLMENT: 'Enrollment',
  ADVISING: 'Advising',
  SYSTEM: 'System',
}

const severityLabels: Record<NotificationSeverity, string> = {
  INFO: 'Info',
  SUCCESS: 'Success',
  WARNING: 'Warning',
  ERROR: 'Error',
}

function formatDateTime(value?: string | null) {
  if (!value) {
    return 'Never'
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function severityTone(severity: NotificationSeverity): BadgeTone {
  if (severity === 'SUCCESS') {
    return 'success'
  }
  if (severity === 'WARNING') {
    return 'warning'
  }
  if (severity === 'ERROR') {
    return 'danger'
  }
  return 'info'
}

function severityAccent(severity: NotificationSeverity): Accent {
  if (severity === 'SUCCESS') {
    return 'success'
  }
  if (severity === 'WARNING') {
    return 'warning'
  }
  if (severity === 'ERROR') {
    return 'danger'
  }
  return 'info'
}

function severityIcon(severity: NotificationSeverity) {
  if (severity === 'SUCCESS') {
    return <CheckCircleIcon className="h-5 w-5" />
  }
  if (severity === 'WARNING' || severity === 'ERROR') {
    return <ExclamationTriangleIcon className="h-5 w-5" />
  }
  return <InformationCircleIcon className="h-5 w-5" />
}

function SummaryCard({
  helper,
  icon,
  title,
  value,
}: {
  helper: string
  icon: ReactNode
  title: string
  value: number
}) {
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-neutral-500">{title}</p>
          <p className="mt-2 font-display text-2xl font-semibold text-neutral-900">{value}</p>
          <p className="mt-1 text-xs text-neutral-500">{helper}</p>
        </div>
        <div className="rounded-lg bg-primary-light p-2 text-primary">{icon}</div>
      </div>
    </Card>
  )
}

function NotificationListItem({
  markReadPending,
  notification,
  onMarkRead,
}: {
  markReadPending: boolean
  notification: NotificationItem
  onMarkRead: (notificationId: string) => void
}) {
  const accent = severityAccent(notification.severity)
  const accentClass = {
    danger: 'border-l-danger bg-red-50/70',
    warning: 'border-l-warning bg-amber-50/70',
    success: 'border-l-success bg-green-50/70',
    info: 'border-l-info bg-sky-50/70',
  }[accent]

  return (
    <div
      className={[
        'rounded-card border border-neutral-200 border-l-4 p-4',
        notification.isRead ? 'border-l-neutral-200 bg-white' : accentClass,
      ].join(' ')}
    >
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex min-w-0 gap-3">
          <div className="mt-0.5 text-primary">{severityIcon(notification.severity)}</div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="font-semibold text-neutral-900">{notification.title}</h3>
              {!notification.isRead ? <span className="h-2 w-2 rounded-full bg-primary" aria-label="Unread" /> : null}
            </div>
            <p className="mt-1 text-sm text-neutral-600">{notification.message}</p>
            <div className="mt-3 flex flex-wrap items-center gap-2">
              <Badge tone="info">{categoryLabels[notification.category]}</Badge>
              <Badge tone={severityTone(notification.severity)}>{severityLabels[notification.severity]}</Badge>
              <span className="text-xs text-neutral-500">{formatDateTime(notification.createdAt)}</span>
            </div>
          </div>
        </div>
        <div className="flex shrink-0 flex-wrap items-center gap-2 lg:justify-end">
          {notification.actionUrl ? (
            <Link
              to={notification.actionUrl}
              className="inline-flex min-h-11 items-center justify-center rounded-lg px-3 text-sm font-semibold text-primary transition-colors hover:bg-primary-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2"
            >
              {notification.actionLabel || 'Open'}
            </Link>
          ) : null}
          {!notification.isRead ? (
            <Button
              variant="secondary"
              size="sm"
              className="min-w-0"
              loading={markReadPending}
              onClick={() => onMarkRead(notification.id)}
            >
              Mark as read
            </Button>
          ) : null}
        </div>
      </div>
    </div>
  )
}

export function NotificationsPage() {
  const [filters, setFilters] = useState<Required<NotificationFilters>>({
    status: 'ALL',
    category: 'ALL',
    severity: 'ALL',
  })
  const summaryQuery = useNotificationSummary()
  const notificationsQuery = useNotifications(filters)
  const markReadMutation = useMarkNotificationRead()
  const markAllMutation = useMarkAllNotificationsRead()
  const summary = summaryQuery.data
  const notifications = notificationsQuery.data ?? []
  const unreadCount = summary?.unreadCount ?? 0

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
        <SummaryCard title="Unread" value={unreadCount} helper="Needs your review" icon={<BellIcon className="h-5 w-5" />} />
        <SummaryCard
          title="Moodle"
          value={summary?.byCategory.MOODLE ?? 0}
          helper="Moodle integration updates"
          icon={<ServerStackIcon className="h-5 w-5" />}
        />
        <SummaryCard
          title="Grades"
          value={summary?.byCategory.GRADES ?? 0}
          helper="Grade release updates"
          icon={<ClipboardDocumentCheckIcon className="h-5 w-5" />}
        />
        <SummaryCard
          title="Enrollment"
          value={summary?.byCategory.ENROLLMENT ?? 0}
          helper="Registration updates"
          icon={<IdentificationIcon className="h-5 w-5" />}
        />
        <SummaryCard
          title="Advising"
          value={summary?.byCategory.ADVISING ?? 0}
          helper="Advising updates"
          icon={<UserGroupIcon className="h-5 w-5" />}
        />
        <SummaryCard
          title="System"
          value={summary?.byCategory.SYSTEM ?? 0}
          helper="System updates"
          icon={<Cog6ToothIcon className="h-5 w-5" />}
        />
      </div>

      {summaryQuery.isLoading ? <Alert title="Loading notifications">Fetching your notification summary.</Alert> : null}

      <Card>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <CardTitle>Notification Center</CardTitle>
            <p className="mt-1 text-sm text-neutral-500">Review academic, Moodle, grades, enrollment, advising, and system updates.</p>
          </div>
          <Button
            variant="secondary"
            loading={markAllMutation.isPending}
            disabled={unreadCount === 0}
            onClick={() => markAllMutation.mutate()}
          >
            Mark all as read
          </Button>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <Select
            id="notification-status"
            label="Status"
            value={filters.status}
            items={statusItems}
            onValueChange={(value) => setFilters((current) => ({ ...current, status: value as NotificationStatusFilter }))}
          />
          <Select
            id="notification-category"
            label="Category"
            value={filters.category}
            items={categoryItems}
            onValueChange={(value) => setFilters((current) => ({ ...current, category: value as NotificationCategory | 'ALL' }))}
          />
          <Select
            id="notification-severity"
            label="Severity"
            value={filters.severity}
            items={severityItems}
            onValueChange={(value) => setFilters((current) => ({ ...current, severity: value as NotificationSeverity | 'ALL' }))}
          />
        </div>

        <div className="mt-6 space-y-3">
          {notificationsQuery.isLoading ? <Alert title="Loading notifications">Fetching your latest updates.</Alert> : null}
          {notificationsQuery.isError ? (
            <Alert title="Could not load notifications" tone="danger">
              Check your connection and session.
            </Alert>
          ) : null}
          {!notificationsQuery.isLoading && !notificationsQuery.isError && notifications.length === 0 ? (
            <EmptyState
              title="No notifications found"
              description="You are all caught up."
              icon={<ShieldCheckIcon className="h-10 w-10" />}
            />
          ) : null}
          {notifications.map((notification) => (
            <NotificationListItem
              key={notification.id}
              notification={notification}
              markReadPending={markReadMutation.isPending && markReadMutation.variables === notification.id}
              onMarkRead={(notificationId) => markReadMutation.mutate(notificationId)}
            />
          ))}
        </div>
      </Card>
    </div>
  )
}
