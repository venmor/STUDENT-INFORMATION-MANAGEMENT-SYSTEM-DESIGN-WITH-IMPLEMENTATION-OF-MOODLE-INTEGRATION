import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createEnrollment, dropEnrollment, getEnrollments, getSectionRoster } from '@/api/enrollments'

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
