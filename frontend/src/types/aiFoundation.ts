export interface AnalyticsETLRun {
  id: string
  status: 'STARTED' | 'SUCCEEDED' | 'FAILED' | 'PARTIAL' | string
  startedAt: string
  completedAt: string | null
  studentsProcessed: number
  snapshotsCreated: number
  snapshotsUpdated: number
  moodleSnapshotsUsed: number
  failureCount: number
  lastError?: string
  dryRun: boolean
}

export interface AnalyticsSummary {
  latestRun: AnalyticsETLRun | null
  studentsWithSnapshots: number
  moodleSnapshotsUsed: number
  averageAttendance: string | number | null
  officialGradeCount: number
  financialFlags: number
  latestMoodleAccessAt: string | null
}

export interface AnalyticsSnapshot {
  id: string
  student: {
    id: string
    studentNumber: string
    fullName: string
    programme: string
  }
  academicYear: string
  semester: string
  programme?: string
  yearOfStudy?: number
  academicStanding?: string
  attendanceAverage: string | number | null
  financialFlagCount: number
  activeEnrollmentCount: number
  draftGradeCount?: number
  officialGradeCount: number
  gpa?: string | number | null
  latestMoodleAccessAt?: string | null
  latestMoodleCourseAccessAt?: string | null
  moodleSnapshotCount: number
  updatedAt: string
}

export interface KnowledgeIngestionRun {
  id: string
  status: 'STARTED' | 'SUCCEEDED' | 'FAILED' | 'PARTIAL' | string
  startedAt: string
  completedAt: string | null
  sourcesProcessed: number
  chunksCreated: number
  chunksUpserted: number
  failureCount: number
  lastError?: string
}

export interface KnowledgeSummary {
  sources: number
  chunks: number
  latestIngestion: KnowledgeIngestionRun | null
  vectorStore: {
    provider: string
    collection: string
    healthy: boolean
    message: string
  }
}

export interface KnowledgeSource {
  id: string
  sourceType: string
  title: string
  description?: string
  sourcePath?: string
  status: string
  visibility: string
  checksumSha256?: string
  chunkCount: number
  updatedAt: string
}

export interface KnowledgeRetrievalResult {
  chunkId: string
  sourceId: string
  sourceTitle: string
  sourceType: string
  score: number
  text: string
}

export interface KnowledgeTestQueryRequest {
  query: string
  limit?: number
  sourceType?: string
}

export interface KnowledgeTestQueryResponse {
  query: string
  generatedAnswer: null
  results: KnowledgeRetrievalResult[]
}
