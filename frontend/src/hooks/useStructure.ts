import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  createDepartment,
  createProgramme,
  createSchool,
  createStream,
  getDepartments,
  getProgrammes,
  getSchools,
  getStreams,
} from '@/api/structure'

export function useSchools() {
  return useQuery({ queryKey: ['structure', 'schools'], queryFn: getSchools })
}

export function useDepartments(schoolId?: string) {
  return useQuery({
    queryKey: ['structure', 'departments', schoolId],
    queryFn: () => getDepartments(schoolId),
  })
}

export function useProgrammes(departmentId?: string) {
  return useQuery({
    queryKey: ['structure', 'programmes', departmentId],
    queryFn: () => getProgrammes(departmentId),
  })
}

export function useStreams(programmeId?: string) {
  return useQuery({
    queryKey: ['structure', 'streams', programmeId],
    queryFn: () => getStreams(programmeId),
  })
}

export function useStructureMutations() {
  const queryClient = useQueryClient()

  return {
    createSchool: useMutation({
      mutationFn: createSchool,
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['structure', 'schools'] }),
    }),
    createDepartment: useMutation({
      mutationFn: createDepartment,
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['structure', 'departments'] }),
    }),
    createProgramme: useMutation({
      mutationFn: createProgramme,
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['structure', 'programmes'] }),
    }),
    createStream: useMutation({
      mutationFn: createStream,
      onSuccess: () => queryClient.invalidateQueries({ queryKey: ['structure', 'streams'] }),
    }),
  }
}
