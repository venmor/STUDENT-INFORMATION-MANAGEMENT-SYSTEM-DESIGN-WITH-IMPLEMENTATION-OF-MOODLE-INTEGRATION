import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  getMoodleCourseMaps,
  getMoodleEngagementRuns,
  getMoodleEngagementSnapshots,
  getMoodleOutboxEvents,
  getMoodleSyncSummary,
  getMoodleUserMaps,
  retryMoodleOutboxEvent,
} from '@/api/moodleSync'
import type { MoodleOutboxFilters } from '@/types/moodleSync'

export function useMoodleSyncSummary() {
  return useQuery({
    queryKey: ['moodle-sync', 'summary'],
    queryFn: getMoodleSyncSummary,
  })
}

export function useMoodleOutboxEvents(filters: MoodleOutboxFilters) {
  return useQuery({
    queryKey: ['moodle-sync', 'outbox-events', filters],
    queryFn: () => getMoodleOutboxEvents(filters),
  })
}

export function useMoodleUserMaps() {
  return useQuery({
    queryKey: ['moodle-sync', 'user-maps'],
    queryFn: getMoodleUserMaps,
  })
}

export function useMoodleCourseMaps() {
  return useQuery({
    queryKey: ['moodle-sync', 'course-maps'],
    queryFn: getMoodleCourseMaps,
  })
}

export function useMoodleEngagementRuns() {
  return useQuery({
    queryKey: ['moodle-sync', 'engagement-runs'],
    queryFn: getMoodleEngagementRuns,
  })
}

export function useMoodleEngagementSnapshots() {
  return useQuery({
    queryKey: ['moodle-sync', 'engagement-snapshots'],
    queryFn: getMoodleEngagementSnapshots,
  })
}

export function useRetryMoodleOutboxEvent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: retryMoodleOutboxEvent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['moodle-sync'] })
    },
  })
}
