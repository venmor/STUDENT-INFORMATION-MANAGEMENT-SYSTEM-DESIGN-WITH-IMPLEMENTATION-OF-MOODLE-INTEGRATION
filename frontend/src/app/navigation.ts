import type { PrimaryRole } from '@/api/contracts'

export interface NavigationItem {
  to: string
  label: string
}

export function getNavigationItems(role: PrimaryRole): NavigationItem[] {
  const common = [{ to: '/account/password', label: 'Security' }]

  switch (role) {
    case 'STUDENT':
      return [
        { to: '/student/overview', label: 'Overview' },
        { to: '/student/grades', label: 'Grades' },
        { to: '/student/registration', label: 'Registration' },
        { to: '/student/corrections', label: 'Corrections' },
        ...common,
      ]
    case 'ADVISOR':
      return [
        { to: '/advisor/overview', label: 'Students' },
        ...common,
      ]
    case 'FACULTY':
      return [
        { to: '/faculty/overview', label: 'Sections' },
        ...common,
      ]
    case 'ADMIN':
      return [
        { to: '/admin/overview', label: 'Overview' },
        { to: '/admin/users', label: 'Users' },
        ...common,
      ]
    default:
      return common
  }
}
