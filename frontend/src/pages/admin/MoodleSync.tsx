import { type ReactNode, useMemo, useState } from 'react'
import {
  AcademicCapIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  CircleStackIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  QueueListIcon,
  RectangleStackIcon,
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
import {
  useMoodleCourseMaps,
  useMoodleEngagementRuns,
  useMoodleEngagementSnapshots,
  useMoodleOutboxEvents,
  useMoodleSyncSummary,
  useMoodleUserMaps,
  useRetryMoodleOutboxEvent,
} from '@/hooks/useMoodleSync'
import type {
  MoodleCourseMap,
  MoodleEngagementRun,
  MoodleEngagementRunStatus,
  MoodleEngagementSnapshot,
  MoodleOutboxEvent,
  MoodleOutboxStatus,
  MoodleSyncSummary,
  MoodleUserMap,
} from '@/types/moodleSync'

type Accent = 'danger' | 'warning' | 'success' | 'info'
type BadgeTone = 'default' | 'success' | 'warning' | 'danger' | 'info'

const statusItems = [
  { label: 'All', value: 'ALL' },
  { label: 'Pending', value: 'PENDING' },
  { label: 'Processed', value: 'PROCESSED' },
  { label: 'Failed', value: 'FAILED' },
]

const eventTypeItems = [
  { label: 'All', value: 'ALL' },
  { label: 'USER_SYNC_REQUESTED', value: 'USER_SYNC_REQUESTED' },
  { label: 'COURSE_SYNC_REQUESTED', value: 'COURSE_SYNC_REQUESTED' },
  { label: 'ENROLLMENT_SYNC_REQUESTED', value: 'ENROLLMENT_SYNC_REQUESTED' },
  { label: 'GRADE_SYNC_REQUESTED', value: 'GRADE_SYNC_REQUESTED' },
]

function formatDateTime(value?: string | null) {
  if (!value) {
    return 'Never'
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function readableEventType(value: string) {
  return value
    .toLowerCase()
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function statusTone(status: MoodleOutboxStatus | MoodleEngagementRunStatus | null): BadgeTone {
  if (status === 'SUCCEEDED' || status === 'PROCESSED') {
    return 'success'
  }
  if (status === 'FAILED') {
    return 'danger'
  }
  if (status === 'PENDING' || status === 'PARTIAL' || status === 'DRY_RUN') {
    return 'warning'
  }
  return 'info'
}

function ingestionAccent(status: MoodleEngagementRunStatus | null): Accent {
  if (status === 'SUCCEEDED') {
    return 'success'
  }
  if (status === 'FAILED') {
    return 'danger'
  }
  if (status === 'PARTIAL' || status === 'DRY_RUN') {
    return 'warning'
  }
  return 'info'
}

function configTone(value: 'present' | 'missing'): BadgeTone {
  return value === 'present' ? 'success' : 'danger'
}

function relatedRecordLabel(event: MoodleOutboxEvent) {
  const summary = event.payloadSummary
  if (summary.userId !== null) {
    return `User ID ${summary.userId}`
  }
  if (summary.enrollmentId) {
    return `Enrollment ID ${summary.enrollmentId}`
  }
  if (summary.gradeId) {
    return `Grade ID ${summary.gradeId}`
  }
  if (summary.studentId && summary.sectionId) {
    return `Student ${summary.studentId} / Section ${summary.sectionId}`
  }
  if (summary.sectionId) {
    return `Section ID ${summary.sectionId}`
  }
  return summary.action ? `Action ${summary.action}` : 'No related record'
}

function safeErrorText(value: string) {
  return value.trim() ? value : 'None'
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
  value: string | number
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

function StatusBadge({ status }: { status: MoodleOutboxStatus | MoodleEngagementRunStatus | null }) {
  const labels: Partial<Record<MoodleOutboxStatus | MoodleEngagementRunStatus, string>> = {
    PENDING: 'Pending',
    PROCESSED: 'Processed',
    FAILED: 'Failed',
    RUNNING: 'Running',
    SUCCEEDED: 'Succeeded',
    PARTIAL: 'Partial',
    DRY_RUN: 'Dry Run',
  }
  return <Badge tone={statusTone(status)}>{status ? labels[status] : 'None'}</Badge>
}

function ReadinessRow({
  detail,
  label,
  tone,
  value,
}: {
  detail?: string
  label: string
  tone?: BadgeTone
  value: string | number
}) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-neutral-100 py-3 last:border-b-0">
      <div>
        <p className="text-sm font-medium text-neutral-900">{label}</p>
        {detail ? <p className="mt-1 text-xs text-neutral-500">{detail}</p> : null}
      </div>
      {tone ? <Badge tone={tone}>{value}</Badge> : <span className="text-sm font-semibold text-neutral-900">{value}</span>}
    </div>
  )
}

function OutboxTable({
  events,
  isLoading,
  onRetry,
  retryingId,
}: {
  events: MoodleOutboxEvent[]
  isLoading: boolean
  onRetry: (event: MoodleOutboxEvent) => void
  retryingId?: string
}) {
  if (isLoading) {
    return <TableSkeleton columns={8} />
  }

  if (events.length === 0) {
    return (
      <EmptyState
        title="No Moodle sync events found"
        description="Create users, sections, enrollments, or official grades to generate sync events."
        icon={<QueueListIcon className="h-10 w-10" />}
      />
    )
  }

  return (
    <DataTable ariaLabel="Integration outbox events">
      <DataTableHead>
        <DataTableRow>
          <DataTableHeader>Event</DataTableHeader>
          <DataTableHeader>Related Record</DataTableHeader>
          <DataTableHeader>Status</DataTableHeader>
          <DataTableHeader>Attempts</DataTableHeader>
          <DataTableHeader>Last Attempt</DataTableHeader>
          <DataTableHeader>Last Error</DataTableHeader>
          <DataTableHeader>Created</DataTableHeader>
          <DataTableHeader>Action</DataTableHeader>
        </DataTableRow>
      </DataTableHead>
      <DataTableBody>
        {events.map((event) => (
          <DataTableRow key={event.id}>
            <DataTableCell>
              <div className="font-medium">{readableEventType(event.eventType)}</div>
              <div className="mt-1 max-w-[9rem] truncate font-mono text-xs text-neutral-500">{event.id}</div>
            </DataTableCell>
            <DataTableCell>{relatedRecordLabel(event)}</DataTableCell>
            <DataTableCell>
              <StatusBadge status={event.status} />
            </DataTableCell>
            <DataTableCell>{event.attempts}</DataTableCell>
            <DataTableCell>{formatDateTime(event.lastAttemptAt)}</DataTableCell>
            <DataTableCell>
              <span className="line-clamp-2 max-w-[16rem] text-neutral-600">{safeErrorText(event.lastError)}</span>
            </DataTableCell>
            <DataTableCell>{formatDateTime(event.createdAt)}</DataTableCell>
            <DataTableCell>
              {event.status === 'FAILED' ? (
                <Button
                  size="sm"
                  onClick={() => onRetry(event)}
                  loading={retryingId === event.id}
                  icon={<ArrowPathIcon className="h-4 w-4" />}
                >
                  Retry
                </Button>
              ) : event.status === 'PENDING' && event.canRetry ? (
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => onRetry(event)}
                  loading={retryingId === event.id}
                  icon={<ArrowPathIcon className="h-4 w-4" />}
                >
                  Process
                </Button>
              ) : (
                <span className="text-sm text-neutral-500">Completed</span>
              )}
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}

function UserMappingsTable({ maps }: { maps: MoodleUserMap[] }) {
  if (maps.length === 0) {
    return <EmptyState title="No Moodle user mappings yet. Run Lane A user sync first." description="" />
  }

  return (
    <DataTable ariaLabel="Moodle user mappings">
      <DataTableHead>
        <DataTableRow>
          <DataTableHeader>SIS User</DataTableHeader>
          <DataTableHeader>SIS User ID</DataTableHeader>
          <DataTableHeader>Moodle User ID</DataTableHeader>
          <DataTableHeader>Moodle Username</DataTableHeader>
          <DataTableHeader>Last Synced</DataTableHeader>
          <DataTableHeader>Created</DataTableHeader>
        </DataTableRow>
      </DataTableHead>
      <DataTableBody>
        {maps.map((mapping) => (
          <DataTableRow key={mapping.id}>
            <DataTableCell>
              <div className="font-medium">{mapping.sisUser.fullName || mapping.sisUser.username}</div>
              <div className="mt-1 text-xs text-neutral-500">{mapping.sisUser.email}</div>
            </DataTableCell>
            <DataTableCell className="font-mono text-xs">{mapping.sisUserId}</DataTableCell>
            <DataTableCell className="font-mono text-xs">{mapping.moodleUserId}</DataTableCell>
            <DataTableCell>{mapping.moodleUsername}</DataTableCell>
            <DataTableCell>{formatDateTime(mapping.lastSyncedAt)}</DataTableCell>
            <DataTableCell>{formatDateTime(mapping.createdAt)}</DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}

function CourseMappingsTable({ maps }: { maps: MoodleCourseMap[] }) {
  if (maps.length === 0) {
    return <EmptyState title="No Moodle course mappings yet. Run Lane A course sync first." description="" />
  }

  return (
    <DataTable ariaLabel="Moodle course mappings">
      <DataTableHead>
        <DataTableRow>
          <DataTableHeader>SIS Section</DataTableHeader>
          <DataTableHeader>Section ID</DataTableHeader>
          <DataTableHeader>Moodle Course ID</DataTableHeader>
          <DataTableHeader>Moodle Shortname</DataTableHeader>
          <DataTableHeader>Category ID</DataTableHeader>
          <DataTableHeader>Grade Target</DataTableHeader>
          <DataTableHeader>Last Synced</DataTableHeader>
        </DataTableRow>
      </DataTableHead>
      <DataTableBody>
        {maps.map((mapping) => (
          <DataTableRow key={mapping.id}>
            <DataTableCell>
              <div className="font-medium">{mapping.sisSection.courseCode}</div>
              <div className="mt-1 text-xs text-neutral-500">
                {mapping.sisSection.courseTitle} / {mapping.sisSection.sectionCode}
              </div>
            </DataTableCell>
            <DataTableCell className="max-w-[9rem] truncate font-mono text-xs">{mapping.sectionId}</DataTableCell>
            <DataTableCell className="font-mono text-xs">{mapping.moodleCourseId}</DataTableCell>
            <DataTableCell>{mapping.moodleShortname}</DataTableCell>
            <DataTableCell>{mapping.moodleCategoryId}</DataTableCell>
            <DataTableCell>
              <Badge tone={mapping.gradeTargetConfigured ? 'success' : 'warning'}>
                {mapping.gradeTargetConfigured ? 'Configured' : 'Missing'}
              </Badge>
            </DataTableCell>
            <DataTableCell>{formatDateTime(mapping.lastSyncedAt)}</DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}

function EngagementRunsTable({ runs }: { runs: MoodleEngagementRun[] }) {
  if (runs.length === 0) {
    return <p className="text-sm text-neutral-500">No engagement ingestion runs yet.</p>
  }

  return (
    <DataTable ariaLabel="Moodle engagement ingestion runs">
      <DataTableHead>
        <DataTableRow>
          <DataTableHeader>Status</DataTableHeader>
          <DataTableHeader>Dry Run</DataTableHeader>
          <DataTableHeader>Started</DataTableHeader>
          <DataTableHeader>Completed</DataTableHeader>
          <DataTableHeader>Courses</DataTableHeader>
          <DataTableHeader>Users</DataTableHeader>
          <DataTableHeader>Snapshots</DataTableHeader>
          <DataTableHeader>Skipped</DataTableHeader>
          <DataTableHeader>Failures</DataTableHeader>
          <DataTableHeader>Last Error</DataTableHeader>
        </DataTableRow>
      </DataTableHead>
      <DataTableBody>
        {runs.map((run) => (
          <DataTableRow key={run.id}>
            <DataTableCell>
              <StatusBadge status={run.status} />
            </DataTableCell>
            <DataTableCell>{run.dryRun ? 'Yes' : 'No'}</DataTableCell>
            <DataTableCell>{formatDateTime(run.startedAt)}</DataTableCell>
            <DataTableCell>{formatDateTime(run.completedAt)}</DataTableCell>
            <DataTableCell>{run.coursesInspected}</DataTableCell>
            <DataTableCell>{run.usersInspected}</DataTableCell>
            <DataTableCell>{run.snapshotsTotal}</DataTableCell>
            <DataTableCell>{run.skippedUnmappedUsers}</DataTableCell>
            <DataTableCell>{run.failureCount}</DataTableCell>
            <DataTableCell>{safeErrorText(run.lastError)}</DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}

function Step34MetricText({ snapshot }: { snapshot: MoodleEngagementSnapshot }) {
  const metricsMissing =
    snapshot.assignmentSubmissionCount === null &&
    snapshot.assignmentSubmissionRate === null &&
    snapshot.quizAttemptCount === null &&
    snapshot.quizAverage === null &&
    snapshot.forumPostCount === null

  return metricsMissing ? (
    <div className="mt-1 text-xs text-neutral-500">Not collected in Step 3.4</div>
  ) : null
}

function EngagementSnapshotsTable({ snapshots }: { snapshots: MoodleEngagementSnapshot[] }) {
  if (snapshots.length === 0) {
    return (
      <EmptyState
        title="No engagement snapshots yet. Run python manage.py ingest_moodle_engagement after Moodle mappings exist."
        description=""
      />
    )
  }

  return (
    <DataTable ariaLabel="Recent Moodle engagement snapshots">
      <DataTableHead>
        <DataTableRow>
          <DataTableHeader>Student/User</DataTableHeader>
          <DataTableHeader>Section</DataTableHeader>
          <DataTableHeader>Moodle User ID</DataTableHeader>
          <DataTableHeader>Moodle Course ID</DataTableHeader>
          <DataTableHeader>Last Moodle Access</DataTableHeader>
          <DataTableHeader>Course Last Access</DataTableHeader>
          <DataTableHeader>Collected</DataTableHeader>
        </DataTableRow>
      </DataTableHead>
      <DataTableBody>
        {snapshots.map((snapshot) => (
          <DataTableRow key={snapshot.id}>
            <DataTableCell>
              <div className="font-medium">{snapshot.studentUser?.fullName ?? snapshot.studentUser?.username ?? 'Unmapped user'}</div>
              <div className="mt-1 text-xs text-neutral-500">
                {snapshot.student?.studentNumber ?? snapshot.studentUser?.email ?? 'No SIS student mapping'}
              </div>
              <Step34MetricText snapshot={snapshot} />
            </DataTableCell>
            <DataTableCell>
              <div className="font-medium">{snapshot.section?.courseCode ?? 'Unmapped section'}</div>
              <div className="mt-1 text-xs text-neutral-500">{snapshot.section?.sectionCode ?? 'No SIS section mapping'}</div>
            </DataTableCell>
            <DataTableCell className="font-mono text-xs">{snapshot.moodleUserId}</DataTableCell>
            <DataTableCell className="font-mono text-xs">{snapshot.moodleCourseId}</DataTableCell>
            <DataTableCell>{formatDateTime(snapshot.moodleLastAccessAt)}</DataTableCell>
            <DataTableCell>{formatDateTime(snapshot.moodleCourseLastAccessAt)}</DataTableCell>
            <DataTableCell>{formatDateTime(snapshot.collectedAt)}</DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}

function MiniMetric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3">
      <p className="text-xs font-medium uppercase text-neutral-500">{label}</p>
      <p className="mt-1 text-sm font-semibold text-neutral-900">{value}</p>
    </div>
  )
}

function buildSummaryCards(summary?: MoodleSyncSummary) {
  const latestStatus = summary?.engagement.latestRunStatus ?? null
  return [
    {
      title: 'Pending Events',
      value: summary?.outbox.pending ?? 0,
      icon: <ClockIcon className="h-5 w-5" />,
      accent: 'warning' as Accent,
      helper: 'Waiting to be processed',
    },
    {
      title: 'Processed Events',
      value: summary?.outbox.processed ?? 0,
      icon: <CheckCircleIcon className="h-5 w-5" />,
      accent: 'success' as Accent,
      helper: 'Completed sync work',
    },
    {
      title: 'Failed Events',
      value: summary?.outbox.failed ?? 0,
      icon: <ExclamationTriangleIcon className="h-5 w-5" />,
      accent: 'danger' as Accent,
      helper: 'Needs admin attention',
    },
    {
      title: 'Retry Queue',
      value: summary?.outbox.retryable ?? 0,
      icon: <ArrowPathIcon className="h-5 w-5" />,
      accent: 'info' as Accent,
      helper: 'Events that can be retried',
    },
    {
      title: 'User Maps',
      value: summary?.mappings.users ?? 0,
      icon: <UserGroupIcon className="h-5 w-5" />,
      accent: 'info' as Accent,
      helper: 'SIS users linked to Moodle',
    },
    {
      title: 'Course Maps',
      value: summary?.mappings.courses ?? 0,
      icon: <RectangleStackIcon className="h-5 w-5" />,
      accent: 'info' as Accent,
      helper: 'SIS sections linked to Moodle',
    },
    {
      title: 'Latest Ingestion',
      value: latestStatus ?? 'None',
      icon: <CircleStackIcon className="h-5 w-5" />,
      accent: ingestionAccent(latestStatus),
      helper: formatDateTime(summary?.engagement.latestRunCompletedAt ?? summary?.engagement.latestRunStartedAt),
    },
  ]
}

export function AdminMoodleSyncPage() {
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [eventTypeFilter, setEventTypeFilter] = useState('ALL')
  const [search, setSearch] = useState('')
  const [feedback, setFeedback] = useState<{ tone: 'success' | 'danger'; message: string } | null>(null)

  const filters = useMemo(
    () => ({ status: statusFilter, eventType: eventTypeFilter, search }),
    [eventTypeFilter, search, statusFilter],
  )
  const summaryQuery = useMoodleSyncSummary()
  const outboxQuery = useMoodleOutboxEvents(filters)
  const userMapsQuery = useMoodleUserMaps()
  const courseMapsQuery = useMoodleCourseMaps()
  const engagementRunsQuery = useMoodleEngagementRuns()
  const engagementSnapshotsQuery = useMoodleEngagementSnapshots()
  const retryMutation = useRetryMoodleOutboxEvent()

  const summary = summaryQuery.data
  const summaryCards = buildSummaryCards(summary)
  const outboxEvents = outboxQuery.data ?? []
  const userMaps = userMapsQuery.data ?? []
  const courseMaps = courseMapsQuery.data ?? []
  const engagementRuns = engagementRunsQuery.data ?? []
  const engagementSnapshots = engagementSnapshotsQuery.data ?? []
  const latestRun = engagementRuns[0]
  const retryingId = retryMutation.isPending ? retryMutation.variables : undefined

  function refreshAll() {
    summaryQuery.refetch()
    outboxQuery.refetch()
    userMapsQuery.refetch()
    courseMapsQuery.refetch()
    engagementRunsQuery.refetch()
    engagementSnapshotsQuery.refetch()
  }

  function retryEvent(event: MoodleOutboxEvent) {
    setFeedback(null)
    retryMutation.mutate(event.id, {
      onSuccess: () => {
        setFeedback({ tone: 'success', message: 'Moodle sync event retry completed.' })
      },
      onError: () => {
        setFeedback({
          tone: 'danger',
          message: 'Moodle sync retry failed. Check the event status and backend logs.',
        })
      },
    })
  }

  return (
    <div className="space-y-6">
      {summaryQuery.isLoading ? (
        <Alert tone="info" title="Loading Moodle sync dashboard">
          Fetching summary, mappings, outbox events, and engagement ingestion state.
        </Alert>
      ) : null}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-7">
        {summaryCards.map((card) => (
          <SummaryCard key={card.title} {...card} />
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(20rem,0.8fr)]">
        <Card>
          <div className="flex items-center gap-2">
            <ShieldCheckIcon className="h-5 w-5 text-primary" />
            <CardTitle>Integration Readiness</CardTitle>
          </div>
          <div className="mt-4">
            <ReadinessRow
              label="Moodle REST configuration"
              value={summary?.readiness.moodleRestConfig === 'present' ? 'Present' : 'Missing'}
              tone={configTone(summary?.readiness.moodleRestConfig ?? 'missing')}
              detail="Base URL and service token configured"
            />
            <ReadinessRow
              label="LTI configuration"
              value={summary?.readiness.ltiConfig === 'present' ? 'Present' : 'Missing'}
              tone={configTone(summary?.readiness.ltiConfig ?? 'missing')}
              detail="Client, deployment, issuer allowlist, and key material configured"
            />
            <ReadinessRow label="User mappings" value={summary?.mappings.users ?? 0} />
            <ReadinessRow label="Course mappings" value={summary?.mappings.courses ?? 0} />
            <ReadinessRow label="Pending outbox events" value={summary?.outbox.pending ?? 0} />
            <ReadinessRow label="Failed outbox events" value={summary?.outbox.failed ?? 0} />
            <ReadinessRow
              label="Latest engagement ingestion"
              value={
                summary?.engagement.latestRunStatus
                  ? `${summary.engagement.latestRunStatus} / ${formatDateTime(summary.engagement.latestRunCompletedAt)}`
                  : 'No ingestion runs yet'
              }
            />
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-2">
            <ServerStackIcon className="h-5 w-5 text-primary" />
            <CardTitle>Operational Notes</CardTitle>
          </div>
          <ul className="mt-4 space-y-3 text-sm text-neutral-700">
            <li>Live Moodle is not required for automated tests.</li>
            <li>Retry actions use the existing Step 3.2 outbox processor.</li>
            <li>Engagement snapshots come from Step 3.4 ingestion.</li>
            <li>This page never displays Moodle tokens, LTI private keys, or raw launch tokens.</li>
          </ul>
        </Card>
      </section>

      <Card>
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <CardTitle>Integration Outbox Events</CardTitle>
            <p className="mt-1 text-sm text-neutral-500">Monitor event state and retry failed or pending Moodle sync work.</p>
          </div>
          <Button variant="secondary" onClick={refreshAll} icon={<ArrowPathIcon className="h-4 w-4" />}>
            Refresh
          </Button>
        </div>
        <div className="mt-5 grid gap-4 lg:grid-cols-[12rem_18rem_minmax(0,1fr)]">
          <Select id="moodle-sync-status-filter" label="Status" value={statusFilter} items={statusItems} onValueChange={setStatusFilter} />
          <Select
            id="moodle-sync-event-type-filter"
            label="Event type"
            value={eventTypeFilter}
            items={eventTypeItems}
            onValueChange={setEventTypeFilter}
          />
          <Input
            id="moodle-sync-search"
            label="Search"
            value={search}
            placeholder="Search event id or related record"
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        {feedback ? (
          <Alert tone={feedback.tone} className="mt-4">
            {feedback.message}
          </Alert>
        ) : null}
        {outboxQuery.isError ? (
          <div className="mt-5">
            <EmptyState
              title="Could not load Moodle sync events"
              description="Check the backend API and your session permissions."
              icon={<ExclamationTriangleIcon className="h-10 w-10" />}
            />
          </div>
        ) : (
          <div className="mt-5">
            <OutboxTable
              events={outboxEvents}
              isLoading={outboxQuery.isLoading}
              onRetry={retryEvent}
              retryingId={retryingId}
            />
          </div>
        )}
      </Card>

      <section className="space-y-4">
        <CardTitle className="text-lg">Moodle Mappings</CardTitle>
        <div className="grid gap-6 xl:grid-cols-2">
          <Card>
            <div className="flex items-center gap-2">
              <UserGroupIcon className="h-5 w-5 text-primary" />
              <CardTitle>User Mappings</CardTitle>
            </div>
            <div className="mt-4">{userMapsQuery.isLoading ? <TableSkeleton columns={6} /> : <UserMappingsTable maps={userMaps} />}</div>
          </Card>
          <Card>
            <div className="flex items-center gap-2">
              <AcademicCapIcon className="h-5 w-5 text-primary" />
              <CardTitle>Course Mappings</CardTitle>
            </div>
            <div className="mt-4">
              {courseMapsQuery.isLoading ? <TableSkeleton columns={7} /> : <CourseMappingsTable maps={courseMaps} />}
            </div>
          </Card>
        </div>
      </section>

      <Card>
        <div className="flex items-center gap-2">
          <CircleStackIcon className="h-5 w-5 text-primary" />
          <CardTitle>Moodle Engagement Ingestion</CardTitle>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-6">
          <MiniMetric label="Latest run status" value={latestRun?.status ?? summary?.engagement.latestRunStatus ?? 'None'} />
          <MiniMetric label="Courses inspected" value={latestRun?.coursesInspected ?? 0} />
          <MiniMetric label="Users inspected" value={latestRun?.usersInspected ?? 0} />
          <MiniMetric label="Snapshots created/updated" value={latestRun?.snapshotsTotal ?? summary?.engagement.latestRunSnapshots ?? 0} />
          <MiniMetric label="Failures" value={latestRun?.failureCount ?? summary?.engagement.latestRunFailures ?? 0} />
          <MiniMetric label="Last completed" value={formatDateTime(latestRun?.completedAt ?? summary?.engagement.latestRunCompletedAt)} />
        </div>
        <div className="mt-6 space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-neutral-900">Ingestion Runs</h3>
            <div className="mt-3">
              {engagementRunsQuery.isLoading ? <TableSkeleton columns={10} /> : <EngagementRunsTable runs={engagementRuns} />}
            </div>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-neutral-900">Recent Snapshots</h3>
            <div className="mt-3">
              {engagementSnapshotsQuery.isLoading ? (
                <TableSkeleton columns={7} />
              ) : (
                <EngagementSnapshotsTable snapshots={engagementSnapshots} />
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card>
        <CardTitle>Current Scope</CardTitle>
        <ul className="mt-4 space-y-3 text-sm text-neutral-700">
          <li>This dashboard monitors Moodle integration state created by Steps 3.2 and 3.4.</li>
          <li>It does not implement notifications; that belongs to Step 3.5B.</li>
          <li>It does not implement admin reports; that belongs to Step 3.5E.</li>
          <li>It does not implement AI at-risk scoring; that belongs to later phases.</li>
          <li>Live Moodle testing remains optional for automated development workflows.</li>
        </ul>
      </Card>
    </div>
  )
}
