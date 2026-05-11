export type MoodleOutboxStatus = 'PENDING' | 'PROCESSED' | 'FAILED'

export type MoodleEngagementRunStatus = 'RUNNING' | 'SUCCEEDED' | 'PARTIAL' | 'FAILED' | 'DRY_RUN'

export interface MoodleSyncSummary {
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
  engagement: {
    latestRunStatus: MoodleEngagementRunStatus | null
    latestRunStartedAt: string | null
    latestRunCompletedAt: string | null
    latestRunSnapshots: number
    latestRunFailures: number
  }
  readiness: {
    moodleRestConfig: 'present' | 'missing'
    ltiConfig: 'present' | 'missing'
  }
}

export interface MoodleOutboxPayloadSummary {
  userId: number | string | null
  sectionId: string | null
  enrollmentId: string | null
  studentId: string | null
  gradeId: string | null
  action: string
}

export interface MoodleOutboxEvent {
  id: string
  eventType: 'USER_SYNC_REQUESTED' | 'COURSE_SYNC_REQUESTED' | 'ENROLLMENT_SYNC_REQUESTED' | 'GRADE_SYNC_REQUESTED' | string
  status: MoodleOutboxStatus
  payloadSummary: MoodleOutboxPayloadSummary
  attempts: number
  lastError: string
  lastAttemptAt: string | null
  processedAt: string | null
  createdAt: string
  canRetry: boolean
}

export interface MoodleUserMap {
  id: string
  sisUser: {
    id: number
    username: string
    fullName: string
    email: string
  }
  sisUserId: number
  moodleUserId: number
  moodleUsername: string
  lastSyncedAt: string
  createdAt: string
}

export interface MoodleCourseMap {
  id: string
  sisSection: {
    id: string
    courseCode: string
    courseTitle: string
    sectionCode: string
  }
  sectionId: string
  moodleCourseId: number
  moodleShortname: string
  moodleCategoryId: number
  gradeTargetConfigured: boolean
  gradeComponent: string
  gradeActivityId: number | null
  gradeItemNumber: number | null
  gradeItemLabel: string
  lastSyncedAt: string
  createdAt: string
}

export interface MoodleEngagementRun {
  id: string
  status: MoodleEngagementRunStatus
  dryRun: boolean
  startedAt: string
  completedAt: string | null
  coursesInspected: number
  usersInspected: number
  snapshotsCreated: number
  snapshotsUpdated: number
  snapshotsTotal: number
  skippedUnmappedUsers: number
  failureCount: number
  lastError: string
}

export interface MoodleEngagementSnapshot {
  id: string
  studentUser: {
    id: number
    username: string
    fullName: string
    email: string
  } | null
  student: {
    id: string
    studentNumber: string
  } | null
  section: {
    id: string
    courseCode: string
    courseTitle: string
    sectionCode: string
  } | null
  moodleUserId: number
  moodleCourseId: number
  moodleLastAccessAt: string | null
  moodleCourseLastAccessAt: string | null
  assignmentSubmissionCount: number | null
  assignmentSubmissionRate: string | null
  quizAttemptCount: number | null
  quizAverage: string | null
  forumPostCount: number | null
  collectedAt: string
  createdAt: string
}

export interface MoodleOutboxFilters {
  status?: string
  eventType?: string
  search?: string
}
