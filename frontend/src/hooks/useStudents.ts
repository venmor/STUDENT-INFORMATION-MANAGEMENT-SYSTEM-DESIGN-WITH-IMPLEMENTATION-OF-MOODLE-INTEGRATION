import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  approveAdvisingNote,
  createAdvisingNote,
  createCorrectionRequest,
  createFinancialFlag,
  getAdvisingNotes,
  getCorrectionRequests,
  getFinancialFlags,
  getStudent,
  getStudents,
  reviewCorrectionRequest,
  updateAdvisingNote,
  updateFinancialFlag,
  updateStudent,
} from '@/api/students'

export function useStudents() {
  return useQuery({
    queryKey: ['students'],
    queryFn: getStudents,
  })
}

export function useStudent(studentId?: string) {
  return useQuery({
    queryKey: ['students', studentId],
    queryFn: () => getStudent(studentId!),
    enabled: Boolean(studentId),
  })
}

export function useFinancialFlags(studentId?: string) {
  return useQuery({
    queryKey: ['students', studentId, 'financial-flags'],
    queryFn: () => getFinancialFlags(studentId!),
    enabled: Boolean(studentId),
  })
}

export function useAdvisingNotes(studentId?: string) {
  return useQuery({
    queryKey: ['students', studentId, 'advising-notes'],
    queryFn: () => getAdvisingNotes(studentId!),
    enabled: Boolean(studentId),
  })
}

export function useCorrectionRequests(studentId?: string) {
  return useQuery({
    queryKey: ['students', studentId, 'correction-requests'],
    queryFn: () => getCorrectionRequests(studentId!),
    enabled: Boolean(studentId),
  })
}

export function useStudentMutations(studentId?: string) {
  const queryClient = useQueryClient()

  function invalidate() {
    return Promise.all([
      queryClient.invalidateQueries({ queryKey: ['students', studentId] }),
      queryClient.invalidateQueries({ queryKey: ['students', studentId, 'financial-flags'] }),
      queryClient.invalidateQueries({ queryKey: ['students', studentId, 'advising-notes'] }),
      queryClient.invalidateQueries({ queryKey: ['students', studentId, 'correction-requests'] }),
      queryClient.invalidateQueries({ queryKey: ['students'] }),
    ])
  }

  return {
    updateStudent: useMutation({
      mutationFn: (payload: Parameters<typeof updateStudent>[1]) => updateStudent(studentId!, payload),
      onSuccess: invalidate,
    }),
    createFinancialFlag: useMutation({
      mutationFn: (payload: Parameters<typeof createFinancialFlag>[1]) => createFinancialFlag(studentId!, payload),
      onSuccess: invalidate,
    }),
    updateFinancialFlag: useMutation({
      mutationFn: ({ flagId, ...payload }: Parameters<typeof updateFinancialFlag>[2] & { flagId: string }) =>
        updateFinancialFlag(studentId!, flagId, payload),
      onSuccess: invalidate,
    }),
    createAdvisingNote: useMutation({
      mutationFn: (noteText: string) => createAdvisingNote(studentId!, noteText),
      onSuccess: invalidate,
    }),
    updateAdvisingNote: useMutation({
      mutationFn: ({ noteId, noteText }: { noteId: string; noteText: string }) =>
        updateAdvisingNote(studentId!, noteId, noteText),
      onSuccess: invalidate,
    }),
    approveAdvisingNote: useMutation({
      mutationFn: (noteId: string) => approveAdvisingNote(studentId!, noteId),
      onSuccess: invalidate,
    }),
    createCorrectionRequest: useMutation({
      mutationFn: (payload: Parameters<typeof createCorrectionRequest>[1]) =>
        createCorrectionRequest(studentId!, payload),
      onSuccess: invalidate,
    }),
    reviewCorrectionRequest: useMutation({
      mutationFn: ({ correctionRequestId, ...payload }: { correctionRequestId: string; status: string; reviewNote: string }) =>
        reviewCorrectionRequest(studentId!, correctionRequestId, payload),
      onSuccess: invalidate,
    }),
  }
}
