import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createGrade, getGrades, officialiseGrade, updateGrade } from '@/api/grades'

export function useGrades(filters?: { studentId?: string }) {
  return useQuery({
    queryKey: ['grades', filters],
    queryFn: () => getGrades(filters),
  })
}

export function useGradeMutations() {
  const queryClient = useQueryClient()

  return {
    createGrade: useMutation({
      mutationFn: createGrade,
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['grades'] }),
    }),
    updateGrade: useMutation({
      mutationFn: ({ gradeId, ...payload }: { gradeId: string; numericScore?: string; specialCode?: string; changeReason?: string }) =>
        updateGrade(gradeId, payload),
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['grades'] }),
    }),
    officialiseGrade: useMutation({
      mutationFn: officialiseGrade,
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['grades'] }),
    }),
  }
}
