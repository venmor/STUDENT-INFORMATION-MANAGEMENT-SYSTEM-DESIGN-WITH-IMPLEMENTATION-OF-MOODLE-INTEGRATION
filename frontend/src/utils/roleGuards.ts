import type { PrimaryRole } from '@/types'

export function canDo(role: PrimaryRole, action: string) {
  const permissions: Record<PrimaryRole, string[]> = {
    STUDENT: ['view:self', 'register:self', 'correct:self'],
    ADVISOR: ['view:advisees', 'edit:advising-notes', 'view:flags'],
    FACULTY: ['view:sections', 'edit:draft-grades', 'mark:attendance'],
    ADMIN: ['view:all', 'edit:users', 'edit:students', 'officialise:grades'],
  }

  return permissions[role].includes(action)
}

export function roleHomePath(role: PrimaryRole) {
  return `/${role.toLowerCase()}`
}
