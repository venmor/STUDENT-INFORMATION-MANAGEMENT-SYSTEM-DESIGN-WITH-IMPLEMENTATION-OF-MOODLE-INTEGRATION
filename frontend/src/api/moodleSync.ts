import { api } from '@/api/axios'
import type {
  MoodleCourseMap,
  MoodleEngagementRun,
  MoodleEngagementSnapshot,
  MoodleOutboxEvent,
  MoodleOutboxFilters,
  MoodleSyncSummary,
  MoodleUserMap,
} from '@/types/moodleSync'

function filterParam(value?: string) {
  return value && value !== 'ALL' ? value : undefined
}

export async function getMoodleSyncSummary() {
  const response = await api.get<MoodleSyncSummary>('/integration/moodle/summary')
  return response.data
}

export async function getMoodleOutboxEvents(filters: MoodleOutboxFilters = {}) {
  const response = await api.get<MoodleOutboxEvent[]>('/integration/moodle/outbox-events', {
    params: {
      status: filterParam(filters.status),
      event_type: filterParam(filters.eventType),
      search: filters.search || undefined,
    },
  })
  return response.data
}

export async function retryMoodleOutboxEvent(eventId: string) {
  const response = await api.post<MoodleOutboxEvent>(`/integration/moodle/outbox-events/${eventId}/retry`)
  return response.data
}

export async function getMoodleUserMaps() {
  const response = await api.get<MoodleUserMap[]>('/integration/moodle/user-maps')
  return response.data
}

export async function getMoodleCourseMaps() {
  const response = await api.get<MoodleCourseMap[]>('/integration/moodle/course-maps')
  return response.data
}

export async function getMoodleEngagementRuns() {
  const response = await api.get<MoodleEngagementRun[]>('/integration/moodle/engagement-runs')
  return response.data
}

export async function getMoodleEngagementSnapshots() {
  const response = await api.get<MoodleEngagementSnapshot[]>('/integration/moodle/engagement-snapshots')
  return response.data
}
