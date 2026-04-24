import type { PrimaryRole } from '@/api/contracts'

export function roleHomePath(role: PrimaryRole) {
  switch (role) {
    case 'STUDENT':
      return '/student/overview'
    case 'ADVISOR':
      return '/advisor/overview'
    case 'FACULTY':
      return '/faculty/overview'
    case 'ADMIN':
      return '/admin/overview'
    default:
      return '/login'
  }
}
