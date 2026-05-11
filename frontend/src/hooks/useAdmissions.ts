import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  approveApplication,
  createApplication,
  getApplication,
  getApplications,
  rejectApplication,
  submitApplication,
  uploadApplicantDocument,
} from '@/api/admissions'
import type { ApplicantCreatePayload, ApplicantDocumentUploadPayload } from '@/types/admissions'

export function useApplications(params?: { status?: string; programme?: string }) {
  return useQuery({
    queryKey: ['admissions', 'applications', params],
    queryFn: () => getApplications(params),
  })
}

export function useApplication(applicantId?: string) {
  return useQuery({
    queryKey: ['admissions', 'application', applicantId],
    queryFn: () => getApplication(applicantId!),
    enabled: Boolean(applicantId),
  })
}

export function useCreateApplication() {
  return useMutation({
    mutationFn: (payload: ApplicantCreatePayload) => createApplication(payload),
  })
}

export function useUploadApplicantDocument() {
  return useMutation({
    mutationFn: (payload: ApplicantDocumentUploadPayload) => uploadApplicantDocument(payload),
  })
}

export function useSubmitApplication() {
  return useMutation({
    mutationFn: (applicantId: string) => submitApplication(applicantId),
  })
}

export function useApproveApplication() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ applicantId, reviewNotes }: { applicantId: string; reviewNotes?: string }) =>
      approveApplication(applicantId, reviewNotes),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admissions'] }),
  })
}

export function useRejectApplication() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ applicantId, reviewNotes }: { applicantId: string; reviewNotes?: string }) =>
      rejectApplication(applicantId, reviewNotes),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admissions'] }),
  })
}
