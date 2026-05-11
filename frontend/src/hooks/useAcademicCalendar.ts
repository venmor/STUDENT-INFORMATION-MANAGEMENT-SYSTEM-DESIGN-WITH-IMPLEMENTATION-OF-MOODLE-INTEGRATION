import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  cancelCalendarEvent,
  createCalendarEvent,
  getCalendarEvent,
  getCalendarEvents,
  getCalendarSummary,
  updateCalendarEvent,
} from '@/api/calendar'
import type { CalendarEventPayload, CalendarFilters } from '@/types/calendar'

export function useCalendarEvents(filters: CalendarFilters = {}) {
  return useQuery({
    queryKey: ['calendar', 'events', filters],
    queryFn: () => getCalendarEvents(filters),
  })
}

export function useCalendarEvent(eventId?: string) {
  return useQuery({
    queryKey: ['calendar', 'events', eventId],
    queryFn: () => getCalendarEvent(eventId ?? ''),
    enabled: Boolean(eventId),
  })
}

export function useCalendarSummary(filters: CalendarFilters = {}) {
  return useQuery({
    queryKey: ['calendar', 'summary', filters],
    queryFn: () => getCalendarSummary(filters),
  })
}

export function useCreateCalendarEvent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createCalendarEvent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar'] })
    },
  })
}

export function useUpdateCalendarEvent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ eventId, payload }: { eventId: string; payload: Partial<CalendarEventPayload> }) =>
      updateCalendarEvent({ eventId, payload }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar'] })
    },
  })
}

export function useCancelCalendarEvent() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: cancelCalendarEvent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['calendar'] })
    },
  })
}
