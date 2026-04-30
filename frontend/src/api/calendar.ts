import { api } from '@/api/axios'
import type { AcademicCalendarEvent, AcademicCalendarSummary, CalendarEventPayload, CalendarFilters } from '@/types/calendar'

function filterParam(value?: string) {
  return value && value !== 'ALL' ? value : undefined
}

export async function getCalendarEvents(filters: CalendarFilters = {}) {
  const response = await api.get<AcademicCalendarEvent[]>('/calendar/events/', {
    params: {
      month: filters.month,
      start: filters.start,
      end: filters.end,
      event_type: filterParam(filters.eventType),
      audience: filterParam(filters.audience),
      semester: filters.semester || undefined,
      academic_year: filters.academicYear || undefined,
      status: filterParam(filters.status),
    },
  })
  return response.data
}

export async function getCalendarEvent(eventId: string) {
  const response = await api.get<AcademicCalendarEvent>(`/calendar/events/${eventId}/`)
  return response.data
}

export async function getCalendarSummary(filters: CalendarFilters = {}) {
  const response = await api.get<AcademicCalendarSummary>('/calendar/summary/', {
    params: {
      event_type: filterParam(filters.eventType),
      audience: filterParam(filters.audience),
      semester: filters.semester || undefined,
      academic_year: filters.academicYear || undefined,
      status: filterParam(filters.status),
    },
  })
  return response.data
}

export async function createCalendarEvent(payload: CalendarEventPayload) {
  const response = await api.post<AcademicCalendarEvent>('/calendar/events/', payload)
  return response.data
}

export async function updateCalendarEvent({ eventId, payload }: { eventId: string; payload: Partial<CalendarEventPayload> }) {
  const response = await api.patch<AcademicCalendarEvent>(`/calendar/events/${eventId}/`, payload)
  return response.data
}

export async function cancelCalendarEvent(eventId: string) {
  const response = await api.post<AcademicCalendarEvent>(`/calendar/events/${eventId}/cancel/`)
  return response.data
}
