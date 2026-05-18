import { type ReactNode, useMemo, useState } from 'react'
import {
  AcademicCapIcon,
  CalendarDaysIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ClipboardDocumentCheckIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

import { Alert } from '@/components/ui/Alert'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import {
  useCalendarEvents,
  useCalendarSummary,
  useCancelCalendarEvent,
  useCreateCalendarEvent,
  useUpdateCalendarEvent,
} from '@/hooks/useAcademicCalendar'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import type {
  AcademicCalendarEvent,
  CalendarAudience,
  CalendarEventPayload,
  CalendarEventType,
  CalendarFilters,
  CalendarPriority,
  CalendarSource,
  CalendarStatus,
  CalendarUrgency,
  CalendarViewMode,
} from '@/types/calendar'
import type { PrimaryRole } from '@/types'
import { cn } from '@/utils/cn'

type BadgeTone = 'default' | 'success' | 'warning' | 'danger' | 'info'
type Accent = 'danger' | 'warning' | 'success' | 'info'

const eventTypeItems = [
  { label: 'All', value: 'ALL' },
  { label: 'Registration Opens', value: 'REGISTRATION_OPEN' },
  { label: 'Registration Deadline', value: 'REGISTRATION_DEADLINE' },
  { label: 'Drop/Add Deadline', value: 'DROP_DEADLINE' },
  { label: 'Exam Period', value: 'EXAM_PERIOD' },
  { label: 'Grade Submission Deadline', value: 'GRADE_SUBMISSION_DEADLINE' },
  { label: 'Term Start', value: 'TERM_START' },
  { label: 'Term End', value: 'TERM_END' },
  { label: 'Moodle Activity', value: 'MOODLE_ACTIVITY' },
  { label: 'Advising', value: 'ADVISING' },
  { label: 'General', value: 'GENERAL' },
]

const audienceItems = [
  { label: 'All', value: 'ALL' },
  { label: 'Students', value: 'STUDENTS' },
  { label: 'Faculty', value: 'FACULTY' },
  { label: 'Advisors', value: 'ADVISORS' },
  { label: 'Admins', value: 'ADMINS' },
]

const priorityItems = [
  { label: 'Low', value: 'LOW' },
  { label: 'Normal', value: 'NORMAL' },
  { label: 'High', value: 'HIGH' },
  { label: 'Critical', value: 'CRITICAL' },
]

const statusItems = [
  { label: 'All', value: 'ALL' },
  { label: 'Active', value: 'ACTIVE' },
  { label: 'Draft', value: 'DRAFT' },
  { label: 'Cancelled', value: 'CANCELLED' },
]

const eventTypeLabels: Record<CalendarEventType, string> = {
  REGISTRATION_OPEN: 'Registration Opens',
  REGISTRATION_DEADLINE: 'Registration Deadline',
  DROP_DEADLINE: 'Drop/Add Deadline',
  EXAM_PERIOD: 'Exam Period',
  GRADE_SUBMISSION_DEADLINE: 'Grade Submission Deadline',
  TERM_START: 'Term Start',
  TERM_END: 'Term End',
  MOODLE_ACTIVITY: 'Moodle Activity',
  ADVISING: 'Advising',
  GENERAL: 'General',
}

const audienceLabels: Record<CalendarAudience, string> = {
  ALL: 'All',
  STUDENTS: 'Students',
  FACULTY: 'Faculty',
  ADVISORS: 'Advisors',
  ADMINS: 'Admins',
}

const priorityLabels: Record<CalendarPriority, string> = {
  LOW: 'Low',
  NORMAL: 'Normal',
  HIGH: 'High',
  CRITICAL: 'Critical',
}

const sourceLabels: Record<CalendarSource, string> = {
  MANUAL: 'Manual',
  COURSE_SECTION: 'Course Section',
  SYSTEM: 'System',
  MOODLE: 'Moodle',
}

const statusLabels: Record<CalendarStatus, string> = {
  ACTIVE: 'Active',
  CANCELLED: 'Cancelled',
  DRAFT: 'Draft',
}

const urgencyLabels: Record<CalendarUrgency, string> = {
  OVERDUE: 'Overdue',
  TODAY: 'Today',
  THIS_WEEK: 'This week',
  UPCOMING: 'Upcoming',
  FUTURE: 'Future',
}

const priorityWeight: Record<CalendarPriority, number> = {
  CRITICAL: 0,
  HIGH: 1,
  NORMAL: 2,
  LOW: 3,
}

function monthParam(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

function formatDateTime(value?: string | null) {
  if (!value) {
    return 'Not set'
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatDate(value: Date | string) {
  const date = typeof value === 'string' ? new Date(value) : value
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(date)
}

function formatTimeRange(event: AcademicCalendarEvent) {
  if (event.allDay) {
    return 'All day'
  }
  const start = new Intl.DateTimeFormat(undefined, { timeStyle: 'short' }).format(new Date(event.startAt))
  if (!event.endAt) {
    return start
  }
  const end = new Intl.DateTimeFormat(undefined, { timeStyle: 'short' }).format(new Date(event.endAt))
  return `${start} - ${end}`
}

function toDateTimeLocal(value?: string | null) {
  if (!value) {
    return ''
  }
  const date = new Date(value)
  const offsetDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000)
  return offsetDate.toISOString().slice(0, 16)
}

function fromDateTimeLocal(value: string) {
  return value ? new Date(value).toISOString() : ''
}

function eventTypeTone(eventType: CalendarEventType): BadgeTone {
  if (eventType === 'REGISTRATION_DEADLINE' || eventType === 'DROP_DEADLINE' || eventType === 'GRADE_SUBMISSION_DEADLINE') {
    return 'warning'
  }
  if (eventType === 'EXAM_PERIOD') {
    return 'danger'
  }
  if (eventType === 'ADVISING' || eventType === 'MOODLE_ACTIVITY') {
    return 'info'
  }
  return 'success'
}

function urgencyTone(urgency: CalendarUrgency): BadgeTone {
  if (urgency === 'OVERDUE') {
    return 'danger'
  }
  if (urgency === 'TODAY' || urgency === 'THIS_WEEK') {
    return 'warning'
  }
  if (urgency === 'UPCOMING') {
    return 'info'
  }
  return 'default'
}

function priorityTone(priority: CalendarPriority): BadgeTone {
  if (priority === 'CRITICAL') {
    return 'danger'
  }
  if (priority === 'HIGH') {
    return 'warning'
  }
  if (priority === 'LOW') {
    return 'default'
  }
  return 'info'
}

function statusTone(status: CalendarStatus): BadgeTone {
  if (status === 'ACTIVE') {
    return 'success'
  }
  if (status === 'CANCELLED') {
    return 'danger'
  }
  return 'warning'
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

function roleDeadlineTypes(role: PrimaryRole): CalendarEventType[] {
  if (role === 'FACULTY') {
    return ['GRADE_SUBMISSION_DEADLINE', 'EXAM_PERIOD', 'MOODLE_ACTIVITY', 'TERM_START', 'TERM_END']
  }
  if (role === 'ADVISOR') {
    return ['ADVISING', 'REGISTRATION_DEADLINE', 'DROP_DEADLINE', 'GENERAL']
  }
  if (role === 'ADMIN') {
    return eventTypeItems.filter((item) => item.value !== 'ALL').map((item) => item.value as CalendarEventType)
  }
  return ['REGISTRATION_DEADLINE', 'DROP_DEADLINE', 'EXAM_PERIOD', 'GENERAL', 'TERM_START', 'TERM_END']
}

function deadlineEventsForRole(events: AcademicCalendarEvent[], role: PrimaryRole) {
  const allowedTypes = new Set(roleDeadlineTypes(role))
  return events
    .filter((event) => allowedTypes.has(event.eventType))
    .filter((event) => (role === 'ADMIN' ? event.priority === 'HIGH' || event.priority === 'CRITICAL' || event.status === 'ACTIVE' : true))
    .sort((left, right) => {
      const priorityDelta = priorityWeight[left.priority] - priorityWeight[right.priority]
      if (priorityDelta !== 0) {
        return priorityDelta
      }
      return new Date(left.startAt).getTime() - new Date(right.startAt).getTime()
    })
    .slice(0, 6)
}

function buildCalendarDays(month: Date) {
  const first = new Date(month.getFullYear(), month.getMonth(), 1)
  const last = new Date(month.getFullYear(), month.getMonth() + 1, 0)
  const leading = first.getDay()
  const days: Array<Date | null> = Array.from({ length: leading }, () => null)
  for (let day = 1; day <= last.getDate(); day += 1) {
    days.push(new Date(month.getFullYear(), month.getMonth(), day))
  }
  while (days.length % 7 !== 0) {
    days.push(null)
  }
  return days
}

function sameLocalDate(date: Date, isoValue: string) {
  const eventDate = new Date(isoValue)
  return date.getFullYear() === eventDate.getFullYear() && date.getMonth() === eventDate.getMonth() && date.getDate() === eventDate.getDate()
}

function EventBadges({ event }: { event: AcademicCalendarEvent }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge tone={eventTypeTone(event.eventType)}>{eventTypeLabels[event.eventType]}</Badge>
      <Badge tone={urgencyTone(event.urgency)}>{urgencyLabels[event.urgency]}</Badge>
      <Badge tone={priorityTone(event.priority)}>{priorityLabels[event.priority]}</Badge>
    </div>
  )
}

function MyDeadlinesPanel({
  events,
  onSelect,
  role,
  selectedId,
}: {
  events: AcademicCalendarEvent[]
  onSelect: (event: AcademicCalendarEvent) => void
  role: PrimaryRole
  selectedId?: string
}) {
  const deadlines = deadlineEventsForRole(events, role)

  return (
    <Card className="p-4">
      <CardTitle>My Deadlines</CardTitle>
      <p className="mt-1 text-sm text-neutral-500">Role-relevant academic dates from the central calendar.</p>
      <div className="mt-4 space-y-3">
        {deadlines.length === 0 ? (
          <p className="text-sm text-neutral-500">No role-specific deadlines match the current filters.</p>
        ) : (
          deadlines.map((event) => (
            <button
              key={event.id}
              type="button"
              onClick={() => onSelect(event)}
              className={cn(
                'w-full rounded-lg border border-neutral-200 bg-white p-3 text-left transition-colors hover:bg-neutral-50',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2',
                selectedId === event.id && 'border-primary bg-primary-light',
              )}
            >
              <p className="font-medium text-neutral-900">{event.title}</p>
              <p className="mt-1 text-xs text-neutral-500">{formatDateTime(event.startAt)}</p>
              <div className="mt-2 flex flex-wrap gap-2">
                <Badge tone={urgencyTone(event.urgency)}>{urgencyLabels[event.urgency]}</Badge>
                <Badge tone={priorityTone(event.priority)}>{priorityLabels[event.priority]}</Badge>
              </div>
            </button>
          ))
        )}
      </div>
    </Card>
  )
}

function MonthView({
  currentMonth,
  events,
  onSelect,
  selectedId,
}: {
  currentMonth: Date
  events: AcademicCalendarEvent[]
  onSelect: (event: AcademicCalendarEvent) => void
  selectedId?: string
}) {
  const days = buildCalendarDays(currentMonth)
  const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  return (
    <div className="overflow-x-auto">
      <div className="min-w-[42rem]">
        <div className="grid grid-cols-7 gap-2 text-xs font-semibold uppercase tracking-wide text-neutral-500">
          {dayLabels.map((day) => (
            <div key={day} className="px-2 py-1">
              {day}
            </div>
          ))}
        </div>
        <div className="mt-2 grid grid-cols-7 gap-2">
          {days.map((day, index) => {
            const dayEvents = day ? events.filter((event) => sameLocalDate(day, event.startAt)) : []
            return (
              <div key={day?.toISOString() ?? `blank-${index}`} className="min-h-28 rounded-lg border border-neutral-200 bg-white p-2">
                {day ? (
                  <>
                    <p className="text-sm font-semibold text-neutral-900">{day.getDate()}</p>
                    <div className="mt-2 space-y-1">
                      {dayEvents.map((event) => (
                        <button
                          key={event.id}
                          type="button"
                          aria-pressed={selectedId === event.id}
                          onClick={() => onSelect(event)}
                          className={cn(
                            'w-full rounded-md border px-2 py-1 text-left text-xs transition-colors',
                            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-1',
                            selectedId === event.id ? 'border-primary bg-primary-light text-primary' : 'border-neutral-200 bg-neutral-50 text-neutral-700',
                          )}
                        >
                          <span className="block truncate font-medium">{event.title}</span>
                          <span className="mt-0.5 block truncate">{eventTypeLabels[event.eventType]}</span>
                          <span className="mt-0.5 block truncate">{urgencyLabels[event.urgency]}</span>
                        </button>
                      ))}
                    </div>
                  </>
                ) : null}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function ListView({
  events,
  onSelect,
  selectedId,
}: {
  events: AcademicCalendarEvent[]
  onSelect: (event: AcademicCalendarEvent) => void
  selectedId?: string
}) {
  const grouped = events.reduce<Record<string, AcademicCalendarEvent[]>>((acc, event) => {
    const key = new Date(event.startAt).toISOString().slice(0, 10)
    acc[key] = [...(acc[key] ?? []), event]
    return acc
  }, {})

  return (
    <div className="space-y-4">
      {Object.entries(grouped).map(([dateKey, dateEvents]) => (
        <div key={dateKey}>
          <h4 className="text-sm font-semibold text-neutral-700">{formatDate(`${dateKey}T00:00:00`)}</h4>
          <div className="mt-2 space-y-2">
            {dateEvents.map((event) => (
              <button
                key={event.id}
                type="button"
                onClick={() => onSelect(event)}
                className={cn(
                  'w-full rounded-lg border border-neutral-200 bg-white p-4 text-left transition-colors hover:bg-neutral-50',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2',
                  selectedId === event.id && 'border-primary bg-primary-light',
                )}
              >
                <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <p className="font-semibold text-neutral-900">{event.title}</p>
                    <p className="mt-1 text-sm text-neutral-500">{formatTimeRange(event)}</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Badge tone={eventTypeTone(event.eventType)}>{eventTypeLabels[event.eventType]}</Badge>
                    <Badge tone="info">{audienceLabels[event.audience]}</Badge>
                    <Badge tone={statusTone(event.status)}>{statusLabels[event.status]}</Badge>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function EventDetails({
  event,
  isAdmin,
  onCancel,
  onEdit,
  onViewFull,
  cancelPending,
}: {
  event?: AcademicCalendarEvent
  isAdmin: boolean
  onCancel: (eventId: string) => void
  onEdit: (event: AcademicCalendarEvent) => void
  onViewFull: (event: AcademicCalendarEvent) => void
  cancelPending: boolean
}) {
  return (
    <Card className="p-4">
      <CardTitle>Event Details</CardTitle>
      {!event ? (
        <p className="mt-3 text-sm text-neutral-500">Select an event to review date, audience, source, and status details.</p>
      ) : (
        <div className="mt-4 space-y-4">
          <div>
            <h4 className="text-lg font-semibold text-neutral-900">{event.title}</h4>
            <div className="mt-3">
              <EventBadges event={event} />
            </div>
          </div>
          <dl className="grid gap-3 text-sm">
            <div>
              <dt className="font-medium text-neutral-500">Date and Time</dt>
              <dd className="mt-1 text-neutral-900">{formatDateTime(event.startAt)}{event.endAt ? ` to ${formatDateTime(event.endAt)}` : ''}</dd>
            </div>
            <div>
              <dt className="font-medium text-neutral-500">Academic Year</dt>
              <dd className="mt-1 text-neutral-900">{event.academicYear}</dd>
            </div>
            <div>
              <dt className="font-medium text-neutral-500">Semester</dt>
              <dd className="mt-1 text-neutral-900">{event.semester}</dd>
            </div>
            <div>
              <dt className="font-medium text-neutral-500">Audience</dt>
              <dd className="mt-1"><Badge tone="info">{audienceLabels[event.audience]}</Badge></dd>
            </div>
            <div>
              <dt className="font-medium text-neutral-500">Status</dt>
              <dd className="mt-1"><Badge tone={statusTone(event.status)}>{statusLabels[event.status]}</Badge></dd>
            </div>
            <div>
              <dt className="font-medium text-neutral-500">Source</dt>
              <dd className="mt-1"><Badge>{sourceLabels[event.source]}</Badge></dd>
            </div>
            {event.location ? (
              <div>
                <dt className="font-medium text-neutral-500">Location</dt>
                <dd className="mt-1 text-neutral-900">{event.location}</dd>
              </div>
            ) : null}
            {event.relatedCourseSectionLabel ? (
              <div>
                <dt className="font-medium text-neutral-500">Related Section</dt>
                <dd className="mt-1 text-neutral-900">{event.relatedCourseSectionLabel}</dd>
              </div>
            ) : null}
            <div>
              <dt className="font-medium text-neutral-500">Description</dt>
              <dd className="mt-1 text-neutral-900">{event.description || 'No description provided.'}</dd>
            </div>
            {isAdmin ? (
              <>
                <div>
                  <dt className="font-medium text-neutral-500">Created</dt>
                  <dd className="mt-1 text-neutral-900">{formatDateTime(event.createdAt)}</dd>
                </div>
                <div>
                  <dt className="font-medium text-neutral-500">Updated</dt>
                  <dd className="mt-1 text-neutral-900">{formatDateTime(event.updatedAt)}</dd>
                </div>
              </>
            ) : null}
          </dl>
          <div className="flex flex-wrap gap-2 border-t border-neutral-100 pt-4">
            <Button variant="outline" size="sm" onClick={() => onViewFull(event)}>
              View full details
            </Button>
            {isAdmin ? (
              <>
                <Button variant="secondary" size="sm" onClick={() => onEdit(event)}>
                  Edit event
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  loading={cancelPending}
                  disabled={event.status === 'CANCELLED'}
                  onClick={() => onCancel(event.id)}
                >
                  Cancel event
                </Button>
              </>
            ) : null}
          </div>
        </div>
      )}
    </Card>
  )
}

const emptyForm = {
  title: '',
  description: '',
  eventType: 'GENERAL' as CalendarEventType,
  audience: 'ALL' as CalendarAudience,
  priority: 'NORMAL' as CalendarPriority,
  academicYear: '',
  semester: '',
  startAt: '',
  endAt: '',
  allDay: false,
  location: '',
  status: 'ACTIVE' as CalendarStatus,
  notifyAffectedUsers: false,
}

function formStateFromEvent(event?: AcademicCalendarEvent) {
  if (!event) {
    return { ...emptyForm }
  }
  return {
    title: event.title,
    description: event.description,
    eventType: event.eventType,
    audience: event.audience,
    priority: event.priority,
    academicYear: event.academicYear,
    semester: event.semester,
    startAt: toDateTimeLocal(event.startAt),
    endAt: toDateTimeLocal(event.endAt),
    allDay: event.allDay,
    location: event.location,
    status: event.status,
    notifyAffectedUsers: false,
  }
}

function CalendarEventForm({
  event,
  onClose,
  onCreate,
  onUpdate,
  open,
  pending,
}: {
  event?: AcademicCalendarEvent
  onClose: () => void
  onCreate: (payload: CalendarEventPayload, options: { onSuccess: () => void }) => void
  onUpdate: (input: { eventId: string; payload: Partial<CalendarEventPayload> }, options: { onSuccess: () => void }) => void
  open: boolean
  pending: boolean
}) {
  const [form, setForm] = useState(formStateFromEvent(event))
  const [errors, setErrors] = useState<string[]>([])

  function updateField<Key extends keyof typeof form>(key: Key, value: (typeof form)[Key]) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  function submit() {
    const nextErrors: string[] = []
    if (!form.title.trim()) {
      nextErrors.push('Title is required.')
    }
    if (!form.academicYear.trim()) {
      nextErrors.push('Academic year is required.')
    }
    if (!form.semester.trim()) {
      nextErrors.push('Semester is required.')
    }
    if (!form.startAt) {
      nextErrors.push('Start date/time is required.')
    }
    if (form.endAt && form.startAt && new Date(form.endAt) < new Date(form.startAt)) {
      nextErrors.push('End date/time must be after the start date/time.')
    }
    setErrors(nextErrors)
    if (nextErrors.length > 0) {
      return
    }

    const payload: CalendarEventPayload = {
      title: form.title.trim(),
      description: form.description.trim(),
      eventType: form.eventType,
      audience: form.audience,
      priority: form.priority,
      academicYear: form.academicYear.trim(),
      semester: form.semester.trim(),
      startAt: fromDateTimeLocal(form.startAt),
      endAt: form.endAt ? fromDateTimeLocal(form.endAt) : null,
      allDay: form.allDay,
      location: form.location.trim(),
      status: form.status,
      source: 'MANUAL',
      relatedCourseSection: null,
      notifyAffectedUsers: form.notifyAffectedUsers,
    }

    if (event) {
      onUpdate({ eventId: event.id, payload }, { onSuccess: onClose })
      return
    }
    onCreate(payload, { onSuccess: onClose })
  }

  return (
    <Modal
      open={open}
      onOpenChange={(nextOpen) => {
        if (!nextOpen) {
          onClose()
        }
      }}
      title={event ? 'Edit Calendar Event' : 'New Calendar Event'}
      description="Create or update one central academic date. Recurring rules and personal reminders are outside Step 3.5D."
    >
      <div className="max-h-[70vh] overflow-y-auto pr-1">
        <div className="space-y-4">
          {errors.length > 0 ? (
            <Alert tone="warning" title="Review event details">
              <ul className="list-disc space-y-1 pl-4">
                {errors.map((error) => (
                  <li key={error}>{error}</li>
                ))}
              </ul>
            </Alert>
          ) : null}
          <Input id="calendar-title" label="Title" value={form.title} onChange={(event) => updateField('title', event.target.value)} />
          <Textarea
            id="calendar-description"
            label="Description"
            value={form.description}
            onChange={(event) => updateField('description', event.target.value)}
          />
          <div className="grid gap-4 sm:grid-cols-2">
            <Select
              id="calendar-event-type"
              label="Event type"
              items={eventTypeItems.filter((item) => item.value !== 'ALL')}
              value={form.eventType}
              onValueChange={(value) => updateField('eventType', value as CalendarEventType)}
            />
            <Select
              id="calendar-audience"
              label="Audience"
              items={audienceItems.filter((item) => item.value !== 'ALL')}
              value={form.audience}
              onValueChange={(value) => updateField('audience', value as CalendarAudience)}
            />
            <Select
              id="calendar-priority"
              label="Priority"
              items={priorityItems}
              value={form.priority}
              onValueChange={(value) => updateField('priority', value as CalendarPriority)}
            />
            <Select
              id="calendar-status"
              label="Event status"
              items={statusItems.filter((item) => item.value !== 'ALL')}
              value={form.status}
              onValueChange={(value) => updateField('status', value as CalendarStatus)}
            />
            <Input
              id="calendar-academic-year"
              label="Academic Year"
              value={form.academicYear}
              onChange={(event) => updateField('academicYear', event.target.value)}
            />
            <Input id="calendar-semester" label="Semester" value={form.semester} onChange={(event) => updateField('semester', event.target.value)} />
            <Input
              id="calendar-start"
              label="Start date/time"
              type="datetime-local"
              value={form.startAt}
              onChange={(event) => updateField('startAt', event.target.value)}
            />
            <Input
              id="calendar-end"
              label="End date/time"
              type="datetime-local"
              value={form.endAt}
              onChange={(event) => updateField('endAt', event.target.value)}
            />
          </div>
          <Input id="calendar-location" label="Location" value={form.location} onChange={(event) => updateField('location', event.target.value)} />
          <label className="flex items-center gap-3 text-sm font-medium text-neutral-700">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-neutral-300 text-primary focus:ring-primary"
              checked={form.allDay}
              onChange={(event) => updateField('allDay', event.target.checked)}
            />
            All day
          </label>
          <label className="flex items-start gap-3 text-sm font-medium text-neutral-700">
            <input
              type="checkbox"
              className="mt-1 h-4 w-4 rounded border-neutral-300 text-primary focus:ring-primary"
              checked={form.notifyAffectedUsers}
              onChange={(event) => updateField('notifyAffectedUsers', event.target.checked)}
            />
            <span>
              Notify affected users
              <span className="mt-1 block text-xs font-normal text-neutral-500">Only high or critical active events create in-app notifications.</span>
            </span>
          </label>
          <div className="flex justify-end gap-2 border-t border-neutral-100 pt-4">
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button loading={pending} onClick={submit}>
              {event ? 'Save changes' : 'Create'}
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  )
}

export function AcademicCalendarPage() {
  const user = useCurrentUser()
  const isAdmin = user?.primaryRole === 'ADMIN'
  const [currentMonth, setCurrentMonth] = useState(() => new Date())
  const [viewMode, setViewMode] = useState<CalendarViewMode>('MONTH')
  const [selectedId, setSelectedId] = useState<string>()
  const [detailModalEvent, setDetailModalEvent] = useState<AcademicCalendarEvent | undefined>()
  const [editingEvent, setEditingEvent] = useState<AcademicCalendarEvent | undefined>()
  const [formOpen, setFormOpen] = useState(false)
  const [filters, setFilters] = useState<Required<Omit<CalendarFilters, 'month' | 'start' | 'end'>>>({
    eventType: 'ALL',
    audience: 'ALL',
    semester: '',
    academicYear: '',
    status: isAdmin ? 'ALL' : 'ACTIVE',
  })
  const effectiveStatus = isAdmin ? filters.status : 'ACTIVE'

  const queryFilters: CalendarFilters = useMemo(
    () => ({
      month: monthParam(currentMonth),
      eventType: filters.eventType,
      audience: filters.audience,
      semester: filters.semester,
      academicYear: filters.academicYear,
      status: effectiveStatus,
    }),
    [currentMonth, effectiveStatus, filters.academicYear, filters.audience, filters.eventType, filters.semester],
  )

  const summaryQuery = useCalendarSummary(filters)
  const eventsQuery = useCalendarEvents(queryFilters)
  const createMutation = useCreateCalendarEvent()
  const updateMutation = useUpdateCalendarEvent()
  const cancelMutation = useCancelCalendarEvent()
  const events = eventsQuery.data ?? []
  const selectedEvent = events.find((event) => event.id === selectedId) ?? events[0]

  const monthLabel = new Intl.DateTimeFormat(undefined, { month: 'long', year: 'numeric' }).format(currentMonth)
  const summary = summaryQuery.data

  function updateFilter<Key extends keyof typeof filters>(key: Key, value: (typeof filters)[Key]) {
    setFilters((current) => ({ ...current, [key]: value }))
  }

  function shiftMonth(delta: number) {
    setCurrentMonth((current) => new Date(current.getFullYear(), current.getMonth() + delta, 1))
  }

  function openCreateForm() {
    setEditingEvent(undefined)
    setFormOpen(true)
  }

  function openEditForm(event: AcademicCalendarEvent) {
    setEditingEvent(event)
    setFormOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <SummaryCard title="Upcoming Events" value={summary?.upcomingCount ?? 0} helper="Visible upcoming dates" accent="info" icon={<CalendarDaysIcon className="h-5 w-5" />} />
        <SummaryCard
          title="Registration Deadlines"
          value={summary?.registrationDeadlines ?? 0}
          helper="Registration close dates"
          accent="warning"
          icon={<ClockIcon className="h-5 w-5" />}
        />
        <SummaryCard title="Exam Periods" value={summary?.examPeriods ?? 0} helper="Scheduled exam windows" accent="danger" icon={<AcademicCapIcon className="h-5 w-5" />} />
        <SummaryCard
          title="Grade Deadlines"
          value={summary?.gradeDeadlines ?? 0}
          helper="Faculty submission dates"
          accent="success"
          icon={<ClipboardDocumentCheckIcon className="h-5 w-5" />}
        />
        <SummaryCard
          title="Next Event"
          value={summary?.nextEvent?.title ?? 'None'}
          helper={summary?.nextEvent ? formatDateTime(summary.nextEvent.startAt) : 'No upcoming event'}
          accent="info"
          icon={<ExclamationTriangleIcon className="h-5 w-5" />}
        />
      </div>

      {eventsQuery.isError || summaryQuery.isError ? (
        <Alert tone="danger" title="Could not load academic calendar">
          Check your connection and session.
        </Alert>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]">
        <div className="space-y-6">
          <Card>
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <CardTitle>Academic Calendar</CardTitle>
                <p className="mt-1 text-sm text-neutral-500">Track central academic dates, deadlines, exam periods, and semester milestones.</p>
              </div>
              <div className="flex flex-wrap gap-2">
                {isAdmin ? (
                  <Button size="sm" onClick={openCreateForm}>
                    New Calendar Event
                  </Button>
                ) : null}
              </div>
            </div>

            <div className="mt-5 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div className="flex flex-wrap items-center gap-2">
                <Button variant="secondary" size="sm" className="min-w-0 px-3" onClick={() => shiftMonth(-1)}>
                  <ChevronLeftIcon className="h-4 w-4" />
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  className="min-w-0 px-3"
                  onClick={() => {
                    setCurrentMonth(new Date())
                  }}
                >
                  Today
                </Button>
                <Button variant="secondary" size="sm" className="min-w-0 px-3" onClick={() => shiftMonth(1)}>
                  Next
                  <ChevronRightIcon className="h-4 w-4" />
                </Button>
                <p className="px-2 text-sm font-semibold text-neutral-700">{monthLabel}</p>
              </div>
              <div className="flex rounded-lg border border-neutral-200 bg-neutral-50 p-1">
                <button
                  type="button"
                  className={cn(
                    'min-h-11 rounded-md px-4 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50',
                    viewMode === 'MONTH' ? 'bg-white text-primary shadow-sm' : 'text-neutral-600 hover:text-primary',
                  )}
                  onClick={() => setViewMode('MONTH')}
                >
                  Month
                </button>
                <button
                  type="button"
                  className={cn(
                    'min-h-11 rounded-md px-4 text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50',
                    viewMode === 'LIST' ? 'bg-white text-primary shadow-sm' : 'text-neutral-600 hover:text-primary',
                  )}
                  onClick={() => setViewMode('LIST')}
                >
                  List
                </button>
              </div>
            </div>

            <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
              <Select
                id="calendar-filter-type"
                label="Type"
                items={eventTypeItems}
                value={filters.eventType}
                onValueChange={(value) => updateFilter('eventType', value as CalendarEventType | 'ALL')}
              />
              <Select
                id="calendar-filter-audience"
                label="Audience"
                items={audienceItems}
                value={filters.audience}
                onValueChange={(value) => updateFilter('audience', value as CalendarAudience | 'ALL')}
              />
              <Input
                id="calendar-filter-semester"
                label="Semester"
                value={filters.semester}
                onChange={(event) => updateFilter('semester', event.target.value)}
              />
              <Input
                id="calendar-filter-academic-year"
                label="Academic Year"
                value={filters.academicYear}
                onChange={(event) => updateFilter('academicYear', event.target.value)}
              />
              <Select
                id="calendar-filter-status"
                label="Status"
                items={isAdmin ? statusItems : statusItems.filter((item) => item.value === 'ACTIVE')}
                value={effectiveStatus}
                onValueChange={(value) => updateFilter('status', value as CalendarStatus | 'ALL')}
              />
            </div>

            <div className="mt-6">
              {events.length === 0 && !eventsQuery.isLoading ? (
                <EmptyState
                  title="No academic calendar events found"
                  description={isAdmin ? 'Create an event or seed demo academic dates.' : 'No academic dates match your current filters.'}
                  icon={<CalendarDaysIcon className="h-10 w-10" />}
                />
              ) : viewMode === 'MONTH' ? (
                <MonthView currentMonth={currentMonth} events={events} selectedId={selectedEvent?.id} onSelect={(event) => { setSelectedId(event.id) }} />
              ) : (
                <ListView events={events} selectedId={selectedEvent?.id} onSelect={(event) => { setSelectedId(event.id) }} />
              )}
            </div>
          </Card>

          <Card>
            <CardTitle>Current Scope</CardTitle>
            <p className="mt-2 text-sm text-neutral-600">
              This calendar tracks central academic dates and deadlines used by enrollment, grading, advising, and student self-service workflows.
            </p>
          </Card>
        </div>

        <div className="space-y-6">
          <MyDeadlinesPanel
            events={events}
            role={user?.primaryRole ?? 'STUDENT'}
            selectedId={selectedEvent?.id}
            onSelect={(event) => setSelectedId(event.id)}
          />
          <EventDetails
            event={selectedEvent}
            isAdmin={Boolean(isAdmin)}
            onEdit={openEditForm}
            onViewFull={(event) => setDetailModalEvent(event)}
            cancelPending={cancelMutation.isPending}
            onCancel={(eventId) => cancelMutation.mutate(eventId)}
          />
        </div>
      </div>

      {isAdmin && formOpen ? (
        <CalendarEventForm
          key={editingEvent?.id ?? 'new-calendar-event'}
          open={formOpen}
          event={editingEvent}
          pending={createMutation.isPending || updateMutation.isPending}
          onClose={() => setFormOpen(false)}
          onCreate={(payload, options) => createMutation.mutate(payload, options)}
          onUpdate={(input, options) => updateMutation.mutate(input, options)}
        />
      ) : null}

      <Modal
        open={!!detailModalEvent}
        onOpenChange={(open) => { if (!open) setDetailModalEvent(undefined) }}
        title={detailModalEvent?.title ?? 'Event Details'}
        description={detailModalEvent ? eventTypeLabels[detailModalEvent.eventType] : ''}
      >
        {detailModalEvent && (
          <div className="space-y-4">
            <EventBadges event={detailModalEvent} />
            <dl className="grid gap-3 text-sm">
              <div>
                <dt className="font-medium text-neutral-500">Date and Time</dt>
                <dd className="mt-1 text-neutral-900">{formatDateTime(detailModalEvent.startAt)}{detailModalEvent.endAt ? ` to ${formatDateTime(detailModalEvent.endAt)}` : ''}</dd>
              </div>
              <div>
                <dt className="font-medium text-neutral-500">Academic Year</dt>
                <dd className="mt-1 text-neutral-900">{detailModalEvent.academicYear}</dd>
              </div>
              <div>
                <dt className="font-medium text-neutral-500">Semester</dt>
                <dd className="mt-1 text-neutral-900">{detailModalEvent.semester}</dd>
              </div>
              <div>
                <dt className="font-medium text-neutral-500">Audience</dt>
                <dd className="mt-1"><Badge tone="info">{audienceLabels[detailModalEvent.audience]}</Badge></dd>
              </div>
              {detailModalEvent.location ? (
                <div>
                  <dt className="font-medium text-neutral-500">Location</dt>
                  <dd className="mt-1 text-neutral-900">{detailModalEvent.location}</dd>
                </div>
              ) : null}
              {detailModalEvent.relatedCourseSectionLabel ? (
                <div>
                  <dt className="font-medium text-neutral-500">Related Section</dt>
                  <dd className="mt-1 text-neutral-900">{detailModalEvent.relatedCourseSectionLabel}</dd>
                </div>
              ) : null}
              <div>
                <dt className="font-medium text-neutral-500">Description</dt>
                <dd className="mt-1 text-neutral-900">{detailModalEvent.description || 'No description provided.'}</dd>
              </div>
            </dl>
            {detailModalEvent.eventType === 'EXAM_PERIOD' && (
              <a href="/documents" className="inline-flex items-center gap-1 text-sm font-semibold text-primary hover:underline">
                View exam documents &rarr;
              </a>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
