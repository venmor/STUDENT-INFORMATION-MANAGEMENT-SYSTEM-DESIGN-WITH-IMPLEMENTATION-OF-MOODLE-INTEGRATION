import { type ReactNode, useState } from 'react'
import {
  ArrowPathIcon,
  BellIcon,
  ClipboardDocumentCheckIcon,
  ExclamationTriangleIcon,
  ServerStackIcon,
  ShieldCheckIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'

import { Alert } from '@/components/ui/Alert'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHead,
  DataTableHeader,
  DataTableRow,
  TableSkeleton,
} from '@/components/ui/Table'
import { useAuditActivity, useAuditSummary } from '@/hooks/useAuditActivity'
import type { AuditCategory, AuditEvent, AuditFilters, AuditSeverity, AuditSummary } from '@/types/audit'

type BadgeTone = 'default' | 'success' | 'warning' | 'danger' | 'info'
type Accent = 'danger' | 'warning' | 'success' | 'info'

const categoryItems = [
  { label: 'All', value: 'ALL' },
  { label: 'User', value: 'USER' },
  { label: 'Student Record', value: 'STUDENT_RECORD' },
  { label: 'Course', value: 'COURSE' },
  { label: 'Enrollment', value: 'ENROLLMENT' },
  { label: 'Grade', value: 'GRADE' },
  { label: 'Moodle', value: 'MOODLE' },
  { label: 'Notification', value: 'NOTIFICATION' },
  { label: 'Academic Calendar', value: 'ACADEMIC_CALENDAR' },
  { label: 'Document', value: 'DOCUMENT' },
  { label: 'LTI', value: 'LTI' },
  { label: 'System', value: 'SYSTEM' },
]

const severityItems = [
  { label: 'All', value: 'ALL' },
  { label: 'Info', value: 'INFO' },
  { label: 'Success', value: 'SUCCESS' },
  { label: 'Warning', value: 'WARNING' },
  { label: 'Error', value: 'ERROR' },
]

const categoryLabels: Record<AuditCategory, string> = {
  USER: 'User',
  STUDENT_RECORD: 'Student Record',
  COURSE: 'Course',
  ENROLLMENT: 'Enrollment',
  GRADE: 'Grade',
  MOODLE: 'Moodle',
  NOTIFICATION: 'Notification',
  ACADEMIC_CALENDAR: 'Academic Calendar',
  DOCUMENT: 'Document',
  LTI: 'LTI',
  SYSTEM: 'System',
}

const severityLabels: Record<AuditSeverity, string> = {
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

function severityTone(severity: AuditSeverity): BadgeTone {
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

function categoryTone(category: AuditCategory): BadgeTone {
  if (category === 'MOODLE' || category === 'LTI') {
    return 'info'
  }
  if (category === 'USER' || category === 'NOTIFICATION') {
    return 'default'
  }
  return 'success'
}

function severityAccent(severity: AuditSeverity): Accent {
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

function shortId(value: string) {
  if (!value) {
    return 'None'
  }
  return value.length > 14 ? `${value.slice(0, 10)}...` : value
}

function actorLabel(event: AuditEvent) {
  if (!event.actor) {
    return 'System'
  }
  return event.actor.fullName || event.actor.username
}

function targetLabel(event: AuditEvent) {
  if (!event.targetType && !event.targetId) {
    return 'None'
  }
  if (!event.targetId) {
    return event.targetType
  }
  return `${event.targetType || 'Target'} ${shortId(event.targetId)}`
}

function metadataEntries(metadata: Record<string, unknown>) {
  return Object.entries(metadata).map(([key, value]) => [
    key,
    typeof value === 'object' && value !== null ? JSON.stringify(value) : String(value),
  ])
}

function SummaryCard({
  accent,
  helper,
  icon,
  title,
  value,
}: {
  accent: Accent
  helper: string
  icon: ReactNode
  title: string
  value: number
}) {
  return (
    <Card accent={accent} className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-medium text-neutral-500">{title}</p>
          <p className="mt-2 truncate font-display text-2xl font-semibold text-neutral-900">{value}</p>
          <p className="mt-1 text-xs text-neutral-500">{helper}</p>
        </div>
        <div className="rounded-lg bg-white p-2 text-primary shadow-sm">{icon}</div>
      </div>
    </Card>
  )
}

function AuditSummaryCards({ summary }: { summary?: AuditSummary }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-7">
      <SummaryCard
        title="Total Events"
        value={summary?.total ?? 0}
        helper="Recorded activity"
        accent="info"
        icon={<ClipboardDocumentCheckIcon className="h-5 w-5" />}
      />
      <SummaryCard
        title="Errors"
        value={summary?.errors ?? 0}
        helper="Needs review"
        accent="danger"
        icon={<ExclamationTriangleIcon className="h-5 w-5" />}
      />
      <SummaryCard
        title="Warnings"
        value={summary?.warnings ?? 0}
        helper="Operational caution"
        accent="warning"
        icon={<ShieldCheckIcon className="h-5 w-5" />}
      />
      <SummaryCard
        title="Today"
        value={summary?.today ?? 0}
        helper="Events today"
        accent="success"
        icon={<ClipboardDocumentCheckIcon className="h-5 w-5" />}
      />
      <SummaryCard
        title="Moodle"
        value={summary?.byCategory.MOODLE ?? 0}
        helper="Sync and LTI activity"
        accent="info"
        icon={<ServerStackIcon className="h-5 w-5" />}
      />
      <SummaryCard
        title="User Activity"
        value={summary?.byCategory.USER ?? 0}
        helper="Account operations"
        accent="info"
        icon={<UserGroupIcon className="h-5 w-5" />}
      />
      <SummaryCard
        title="Notifications"
        value={summary?.byCategory.NOTIFICATION ?? 0}
        helper="Notification actions"
        accent="info"
        icon={<BellIcon className="h-5 w-5" />}
      />
    </div>
  )
}

function AuditTable({
  events,
  isLoading,
  onSelect,
}: {
  events: AuditEvent[]
  isLoading: boolean
  onSelect: (event: AuditEvent) => void
}) {
  if (isLoading) {
    return <TableSkeleton columns={8} />
  }

  if (events.length === 0) {
    return (
      <EmptyState
        title="No audit activity found"
        description="Activity will appear here when users, Moodle sync, notifications, and governed actions occur."
      />
    )
  }

  return (
    <DataTable ariaLabel="Admin activity events">
      <DataTableHead>
        <DataTableRow>
          <DataTableHeader>Time</DataTableHeader>
          <DataTableHeader>Category</DataTableHeader>
          <DataTableHeader>Severity</DataTableHeader>
          <DataTableHeader>Action</DataTableHeader>
          <DataTableHeader>Summary</DataTableHeader>
          <DataTableHeader>Actor</DataTableHeader>
          <DataTableHeader>Target</DataTableHeader>
          <DataTableHeader>Details</DataTableHeader>
        </DataTableRow>
      </DataTableHead>
      <DataTableBody>
        {events.map((event) => (
          <DataTableRow key={event.id}>
            <DataTableCell className="whitespace-nowrap text-neutral-600">{formatDateTime(event.createdAt)}</DataTableCell>
            <DataTableCell>
              <Badge tone={categoryTone(event.category)}>{categoryLabels[event.category]}</Badge>
            </DataTableCell>
            <DataTableCell>
              <Badge tone={severityTone(event.severity)}>{severityLabels[event.severity]}</Badge>
            </DataTableCell>
            <DataTableCell>
              <span className="font-mono text-xs text-neutral-800">{event.action}</span>
            </DataTableCell>
            <DataTableCell className="max-w-sm">
              <p className="line-clamp-2 text-neutral-700">{event.summary}</p>
            </DataTableCell>
            <DataTableCell>{actorLabel(event)}</DataTableCell>
            <DataTableCell>
              <span className="font-mono text-xs text-neutral-700">{targetLabel(event)}</span>
            </DataTableCell>
            <DataTableCell>
              <Button variant="secondary" size="sm" className="min-w-0" onClick={() => onSelect(event)}>
                Details
              </Button>
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}

function ActivityDetails({ event, onClose }: { event: AuditEvent | null; onClose: () => void }) {
  if (!event) {
    return (
      <Card>
        <CardTitle>Activity Details</CardTitle>
        <p className="mt-2 text-sm text-neutral-600">Select an audit event to review sanitized details.</p>
      </Card>
    )
  }

  const entries = metadataEntries(event.metadata)

  return (
    <Card accent={severityAccent(event.severity)}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <CardTitle>Activity Details</CardTitle>
          <p className="mt-1 text-sm text-neutral-600">{event.summary}</p>
        </div>
        <Button variant="ghost" size="sm" className="min-w-0" onClick={onClose}>
          Close
        </Button>
      </div>
      <dl className="mt-5 grid gap-4 md:grid-cols-2">
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Action</dt>
          <dd className="mt-1 font-mono text-sm text-neutral-900">{event.action}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Category</dt>
          <dd className="mt-1">
            <Badge tone={categoryTone(event.category)}>{categoryLabels[event.category]}</Badge>
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Severity</dt>
          <dd className="mt-1">
            <Badge tone={severityTone(event.severity)}>{severityLabels[event.severity]}</Badge>
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Actor</dt>
          <dd className="mt-1 text-sm text-neutral-900">{actorLabel(event)}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Target Type</dt>
          <dd className="mt-1 text-sm text-neutral-900">{event.targetType || 'None'}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Target ID</dt>
          <dd className="mt-1 font-mono text-sm text-neutral-900">{event.targetId || 'None'}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Created</dt>
          <dd className="mt-1 text-sm text-neutral-900">{formatDateTime(event.createdAt)}</dd>
        </div>
      </dl>

      <div className="mt-6">
        <h4 className="text-sm font-semibold text-neutral-900">Sanitized Metadata</h4>
        {entries.length === 0 ? (
          <p className="mt-2 text-sm text-neutral-600">No metadata recorded.</p>
        ) : (
          <div className="mt-3 overflow-hidden rounded-lg border border-neutral-200">
            {entries.map(([key, value]) => (
              <div key={key} className="grid gap-2 border-b border-neutral-100 p-3 last:border-b-0 md:grid-cols-[12rem_1fr]">
                <span className="font-mono text-xs text-neutral-500">{key}</span>
                <span className="break-words text-sm text-neutral-800">{value}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  )
}

export function AdminAuditLogPage() {
  const [filters, setFilters] = useState<Required<Pick<AuditFilters, 'category' | 'severity'>> & { search: string }>({
    category: 'ALL',
    severity: 'ALL',
    search: '',
  })
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null)
  const summaryQuery = useAuditSummary()
  const activityQuery = useAuditActivity({
    category: filters.category,
    severity: filters.severity,
    search: filters.search,
  })
  const events = activityQuery.data ?? []

  return (
    <div className="space-y-6">
      {summaryQuery.isLoading ? (
        <Alert title="Loading audit activity">Fetching admin activity summary.</Alert>
      ) : null}

      <AuditSummaryCards summary={summaryQuery.data} />

      <Card>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <CardTitle>Admin Activity Viewer</CardTitle>
            <p className="mt-1 text-sm text-neutral-600">
              Read-only timeline of important SIS, Moodle, notification, and governance activity.
            </p>
          </div>
          <Button
            variant="secondary"
            icon={<ArrowPathIcon className="h-4 w-4" />}
            onClick={() => {
              summaryQuery.refetch()
              activityQuery.refetch()
            }}
          >
            Refresh
          </Button>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <Select
            id="audit-category"
            label="Category"
            items={categoryItems}
            value={filters.category}
            onValueChange={(value) => setFilters((current) => ({ ...current, category: value as AuditCategory | 'ALL' }))}
          />
          <Select
            id="audit-severity"
            label="Severity"
            items={severityItems}
            value={filters.severity}
            onValueChange={(value) => setFilters((current) => ({ ...current, severity: value as AuditSeverity | 'ALL' }))}
          />
          <Input
            id="audit-search"
            label="Action search"
            placeholder="Search actor, action, summary, or target"
            value={filters.search}
            onChange={(event) => setFilters((current) => ({ ...current, search: event.target.value }))}
          />
        </div>

        {activityQuery.isError ? (
          <div className="mt-6">
            <Alert title="Could not load audit activity" tone="danger">
              Check the backend API and your admin session.
            </Alert>
          </div>
        ) : null}

        <div className="mt-6">
          <AuditTable events={events} isLoading={activityQuery.isLoading} onSelect={setSelectedEvent} />
        </div>
      </Card>

      <ActivityDetails event={selectedEvent} onClose={() => setSelectedEvent(null)} />

      <Card>
        <CardTitle>Current Scope</CardTitle>
        <div className="mt-3 space-y-2 text-sm text-neutral-600">
          <p>This viewer is read-only.</p>
          <p>It covers admin activity, Moodle sync activity, notification activity, and safe LTI/system events where hooks exist.</p>
          <p>It supports Objective 1 verification by showing administrative, SIS, Moodle, and LTI activity recorded by the system.</p>
        </div>
      </Card>
    </div>
  )
}
