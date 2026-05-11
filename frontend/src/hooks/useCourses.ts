import { useQuery } from '@tanstack/react-query'

import { getCourses, getSection, getSections } from '@/api/courses'

export function useCourses() {
  return useQuery({
    queryKey: ['courses'],
    queryFn: getCourses,
  })
}

export function useSections() {
  return useQuery({
    queryKey: ['sections'],
    queryFn: getSections,
  })
}

export function useSection(sectionId?: string) {
  return useQuery({
    queryKey: ['sections', sectionId],
    queryFn: () => getSection(sectionId!),
    enabled: Boolean(sectionId),
  })
}
