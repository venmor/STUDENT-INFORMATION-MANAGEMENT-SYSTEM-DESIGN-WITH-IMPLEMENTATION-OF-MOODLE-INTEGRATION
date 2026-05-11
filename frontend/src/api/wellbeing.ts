import { api } from './axios'

export interface WellbeingConsent {
  id: string
  is_enabled: boolean
  consented_at: string | null
  updated_at: string
}

export interface WellbeingCheckIn {
  id: string
  mood_rating: number
  comment?: string
  triage_class: 'NORMAL' | 'CONCERNING' | 'ESCALATE'
  created_at: string
}

export interface WellbeingHistoryItem {
  id: string
  mood_rating: number
  triage_class: 'NORMAL' | 'CONCERNING' | 'ESCALATE'
  created_at: string
}

export interface CoordinatorAlert {
  id: string
  student_name: string
  student_number: string
  mood_rating: number
  created_at: string
}

export const wellbeingApi = {
  getConsent: () => api.get<WellbeingConsent>('/wellbeing/consent').then((r) => r.data),
  updateConsent: (is_enabled: boolean) =>
    api.post<WellbeingConsent>('/wellbeing/consent', { is_enabled }).then((r) => r.data),
  submitTriage: (data: { mood_rating: number; comment?: string }) =>
    api.post<WellbeingCheckIn>('/ai/wellbeing/triage', data).then((r) => r.data),
  getHistory: () => api.get<WellbeingHistoryItem[]>('/wellbeing/history').then((r) => r.data),
  deleteCheckIn: (id: string) => api.delete(`/wellbeing/history/${id}`),
  purgeHistory: () => api.delete('/wellbeing/history/purge'),
  getCoordinatorAlerts: () => api.get<CoordinatorAlert[]>('/wellbeing/coordinator/alerts').then((r) => r.data),
}
