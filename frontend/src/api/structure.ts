import { api } from '@/api/axios'
import type { Department, Programme, School, Stream } from '@/types/structure'

export async function getSchools() {
  const response = await api.get<School[]>('/structure/schools')
  return response.data
}

export async function createSchool(payload: { code: string; name: string }) {
  const response = await api.post<School>('/structure/schools', payload)
  return response.data
}

export async function getDepartments(schoolId?: string) {
  const params = schoolId ? { school: schoolId } : {}
  const response = await api.get<Department[]>('/structure/departments', { params })
  return response.data
}

export async function createDepartment(payload: { code: string; name: string; school: string }) {
  const response = await api.post<Department>('/structure/departments', payload)
  return response.data
}

export async function getProgrammes(departmentId?: string) {
  const params = departmentId ? { department: departmentId } : {}
  const response = await api.get<Programme[]>('/structure/programmes', { params })
  return response.data
}

export async function createProgramme(payload: { code: string; name: string; department: string; level: string; duration_years: number }) {
  const response = await api.post<Programme>('/structure/programmes', payload)
  return response.data
}

export async function getStreams(programmeId?: string) {
  const params = programmeId ? { programme: programmeId } : {}
  const response = await api.get<Stream[]>('/structure/streams', { params })
  return response.data
}

export async function createStream(payload: { code: string; name: string; programme: string }) {
  const response = await api.post<Stream>('/structure/streams', payload)
  return response.data
}
