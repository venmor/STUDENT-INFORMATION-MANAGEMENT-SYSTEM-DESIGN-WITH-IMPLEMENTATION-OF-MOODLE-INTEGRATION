export interface ReportFilters {
  academicYear?: string
  semester?: string
  programme?: string
  course?: string
  status?: string
}

export interface ProgrammeBreakdown {
  programme: string
  total: number
  active: number
  inactive: number
  percentage: number
}

export interface AdminReportSummary {
  students: {
    total: number
    active: number
    inactive: number
    byProgramme: ProgrammeBreakdown[]
  }
  enrollments: {
    total: number
    currentTerm: number
    pending: number
    confirmed: number
    dropped: number
  }
  capacity: {
    sectionsTotal: number
    sectionsNearCapacity: number
    sectionsFull: number
    averageFillRate: number
  }
  grades: {
    draft: number
    official: number
    pendingApproval: number
    completionRate: number
  }
  moodle: {
    pendingEvents: number
    failedEvents: number
    processedEvents: number
    userMappings: number
    courseMappings: number
    latestEngagementRunStatus: string | null
  }
  calendar: {
    upcomingDeadlines: number
    criticalDeadlines: number
    nextDeadlineTitle: string | null
    nextDeadlineAt: string | null
  }
  activity: {
    auditEventsToday: number
    unreadAdminNotifications: number
  }
}

export interface EnrollmentStatusBreakdown {
  status: string
  label: string
  count: number
}

export interface EnrollmentReport {
  total: number
  statusBreakdown: EnrollmentStatusBreakdown[]
  byProgramme: Array<{ programme: string; count: number }>
  byCourseSection: Array<{
    sectionId: string
    courseCode: string
    courseTitle: string
    sectionCode: string
    academicYear: string
    semester: string
    enrolledCount: number
    totalEnrollments: number
  }>
  topSections: Array<{
    sectionId: string
    courseCode: string
    courseTitle: string
    sectionCode: string
    academicYear: string
    semester: string
    enrolledCount: number
    totalEnrollments: number
  }>
  recentActivity: Array<{
    id: string
    eventType: string
    studentNumber: string
    studentName: string
    courseCode: string
    sectionCode: string
    actor: string
    createdAt: string
  }>
}

export interface CapacitySectionReport {
  sectionId: string
  courseCode: string
  courseTitle: string
  sectionCode: string
  academicYear: string
  semester: string
  facultyName: string
  capacity: number
  enrolledCount: number
  remainingSeats: number
  fillRate: number
  status: string
}

export interface CapacityReport {
  sections: CapacitySectionReport[]
  nearOrFullSections: CapacitySectionReport[]
  summary: {
    sectionsTotal: number
    sectionsNearCapacity: number
    sectionsFull: number
    averageFillRate: number
  }
}

export interface GradeSectionReport {
  sectionId: string
  courseCode: string
  courseTitle: string
  sectionCode: string
  facultyName: string
  academicYear: string
  semester: string
  enrolledCount: number
  draft: number
  official: number
  pendingApproval: number
  missingSubmissions: number
  completionRate: number
  status: string
}

export interface GradeReport {
  totals: {
    draft: number
    official: number
    pendingApproval: number
    completionRate: number
    sectionsWithMissingSubmissions: number
  }
  statusBreakdown: Array<{ status: string; label: string; count: number }>
  sections: GradeSectionReport[]
  sectionsWithMissingSubmissions: GradeSectionReport[]
}

export interface MoodleSyncReport {
  outbox: {
    pending: number
    processed: number
    failed: number
    retryable: number
  }
  mappings: {
    users: number
    courses: number
  }
  latestFailedEvent: {
    id: string
    eventType: string
    attempts: number
    lastError: string
    lastAttemptAt: string | null
    createdAt: string
  } | null
  latestEngagementRun: {
    id: string
    status: string
    dryRun: boolean
    startedAt: string
    completedAt: string | null
    coursesInspected: number
    usersInspected: number
    snapshotsTotal: number
    failureCount: number
    lastError: string
  } | null
  recentIngestionFailures: Array<{
    id: string
    status: string
    dryRun: boolean
    startedAt: string
    completedAt: string | null
    coursesInspected: number
    usersInspected: number
    snapshotsTotal: number
    failureCount: number
    lastError: string
  }>
}

export interface CalendarDeadline {
  id: string
  title: string
  eventType: string
  priority: string
  academicYear: string
  semester: string
  startAt: string
}

export interface CalendarDeadlineReport {
  upcomingNext7Days: number
  upcomingNext30Days: number
  criticalDeadlines: number
  highPriorityEvents: number
  registrationDeadlines: number
  examPeriods: number
  gradeSubmissionDeadlines: number
  nextDeadline: CalendarDeadline | null
  deadlines: CalendarDeadline[]
}

export interface ActivityReport {
  unreadAdminNotifications: number
  auditEventsToday: number
  auditWarnings: number
  auditErrors: number
  byCategory: Record<string, number>
  commonCategories: Array<{ category: string; count: number }>
  recentHighSeverityAuditEvents: Array<{
    id: string
    category: string
    action: string
    severity: string
    summary: string
    createdAt: string
  }>
  riskIndicators: Array<{
    label: string
    count: number
    severity: string
    actionUrl: string
  }>
}
