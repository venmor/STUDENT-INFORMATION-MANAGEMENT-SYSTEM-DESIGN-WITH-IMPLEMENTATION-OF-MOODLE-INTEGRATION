import { api } from '@/api/axios'
import type { Course, CourseSection } from '@/types'

export async function getCourses() {
  const response = await api.get<Course[]>('/courses')
  return response.data
}

export async function getSections() {
  const response = await api.get<CourseSection[]>('/sections')
  return response.data
}

export async function getSection(sectionId: string) {
  const response = await api.get<CourseSection>(`/sections/${sectionId}`)
  return response.data
}
