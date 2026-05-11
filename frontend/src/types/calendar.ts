export type CalendarEventType =
  | 'REGISTRATION_OPEN'
  | 'REGISTRATION_DEADLINE'
  | 'DROP_DEADLINE'
  | 'EXAM_PERIOD'
  | 'GRADE_SUBMISSION_DEADLINE'
  | 'TERM_START'
  | 'TERM_END'
  | 'MOODLE_ACTIVITY'
  | 'ADVISING'
  | 'GENERAL'

export type CalendarAudience = 'ALL' | 'STUDENTS' | 'FACULTY' | 'ADVISORS' | 'ADMINS'
export type CalendarPriority = 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL'
export type CalendarSource = 'MANUAL' | 'COURSE_SECTION' | 'SYSTEM' | 'MOODLE'
export type CalendarStatus = 'ACTIVE' | 'CANCELLED' | 'DRAFT'
export type CalendarUrgency = 'OVERDUE' | 'TODAY' | 'THIS_WEEK' | 'UPCOMING' | 'FUTURE'
export type CalendarViewMode = 'MONTH' | 'LIST'

export interface AcademicCalendarEvent {
  id: string
  title: string
  description: string
  eventType: CalendarEventType
  audience: CalendarAudience
  priority: CalendarPriority
  academicYear: string
  semester: string
  startAt: string
  endAt: string | null
  allDay: boolean
  location: string
  status: CalendarStatus
  source: CalendarSource
  relatedCourseSection: string | null
  relatedCourseSectionLabel: string | null
  urgency: CalendarUrgency
  metadata: Record<string, unknown>
  createdAt: string
  updatedAt: string
}

export interface AcademicCalendarSummary {
  upcomingCount: number
  registrationDeadlines: number
  examPeriods: number
  gradeDeadlines: number
  currentAcademicYear: string
  currentSemester: string
  nextEvent: {
    id: string
    title: string
    startAt: string
  } | null
}

export interface CalendarFilters {
  month?: string
  start?: string
  end?: string
  eventType?: CalendarEventType | 'ALL'
  audience?: CalendarAudience | 'ALL'
  semester?: string
  academicYear?: string
  status?: CalendarStatus | 'ALL'
}

export interface CalendarEventPayload {
  title: string
  description?: string
  eventType: CalendarEventType
  audience: CalendarAudience
  priority?: CalendarPriority
  academicYear: string
  semester: string
  startAt: string
  endAt?: string | null
  allDay?: boolean
  location?: string
  status?: CalendarStatus
  source?: CalendarSource
  relatedCourseSection?: string | null
  metadata?: Record<string, unknown>
  notifyAffectedUsers?: boolean
}
