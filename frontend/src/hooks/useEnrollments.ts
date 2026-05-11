import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  approvePendingRegistration,
  createEnrollment,
  createPendingRegistration,
  dropEnrollment,
  getEnrollments,
  getPendingRegistrations,
  getSectionRoster,
  rejectPendingRegistration,
} from '@/api/enrollments'

export function useEnrollments(filters?: {
  studentId?: string
  sectionId?: string
  includeInactive?: boolean
}) {
  return useQuery({
    queryKey: ['enrollments', filters],
    queryFn: () => getEnrollments(filters),
  })
}

export function useSectionRoster(sectionId?: string) {
  return useQuery({
    queryKey: ['sections', sectionId, 'roster'],
    queryFn: () => getSectionRoster(sectionId!),
    enabled: Boolean(sectionId),
  })
}

export function useEnrollmentMutations() {
  const queryClient = useQueryClient()

  return {
    createEnrollment: useMutation({
      mutationFn: createEnrollment,
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['enrollments'] }),
    }),
    dropEnrollment: useMutation({
      mutationFn: ({ enrollmentId, reason }: { enrollmentId: string; reason?: string }) =>
        dropEnrollment(enrollmentId, reason),
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['enrollments'] }),
    }),
  }
}

export function usePendingRegistrations() {
  return useQuery({
    queryKey: ['registrations', 'pending'],
    queryFn: getPendingRegistrations,
  })
}

export function usePendingRegistrationMutations() {
  const queryClient = useQueryClient()

  return {
    createPending: useMutation({
      mutationFn: createPendingRegistration,
      onSuccess: () =>
        Promise.all([
          queryClient.invalidateQueries({ queryKey: ['registrations'] }),
          queryClient.invalidateQueries({ queryKey: ['enrollments'] }),
        ]),
    }),
    approve: useMutation({
      mutationFn: (enrollmentId: string) => approvePendingRegistration(enrollmentId),
      onSuccess: () =>
        Promise.all([
          queryClient.invalidateQueries({ queryKey: ['registrations'] }),
          queryClient.invalidateQueries({ queryKey: ['enrollments'] }),
        ]),
    }),
    reject: useMutation({
      mutationFn: ({ enrollmentId, reason }: { enrollmentId: string; reason?: string }) =>
        rejectPendingRegistration(enrollmentId, reason),
      onSuccess: () =>
        Promise.all([
          queryClient.invalidateQueries({ queryKey: ['registrations'] }),
          queryClient.invalidateQueries({ queryKey: ['enrollments'] }),
        ]),
    }),
  }
}
