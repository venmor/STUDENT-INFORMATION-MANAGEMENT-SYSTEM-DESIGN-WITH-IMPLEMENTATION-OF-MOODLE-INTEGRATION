import type { PrimaryRole } from '@/types'

export interface LtiSisUser {
  id: string
  username: string
  fullName: string
  email: string
  primaryRole: PrimaryRole
}

export interface LtiLaunchContext {
  issuer: string
  clientId: string
  deploymentId: string
  moodleSubject: string
  moodleUserId: string
  moodleCourseId: string
  roles: string[]
  context: {
    id?: string
    label?: string
    title?: string
  }
  resourceLink: {
    id?: string
    title?: string
  }
  targetLinkUri: string
}

export interface LtiSection {
  id: string
  courseCode: string
  courseTitle: string
  sectionCode: string
  semester: string
  academicYear: string
  faculty: string
  capacity: number
}

export interface LtiRosterEntry {
  studentId: string
  studentNumber: string
  fullName: string
  email: string
  enrollmentStatus: string
}

export interface LtiStudent {
  id: string
  studentNumber: string
  fullName: string
  email: string
  programme: string
  yearOfStudy: number
  academicStanding: string
}

export interface LtiEnrollment {
  enrollmentId: string
  sectionId: string
  courseCode: string
  courseTitle: string
  sectionCode: string
  semester: string
  academicYear: string
  enrollmentStatus: string
}

export interface LtiSessionContext {
  tool: 'advising-dashboard' | 'registration'
  isMapped: boolean
  launch: LtiLaunchContext
  sisUser: LtiSisUser | null
  section: LtiSection | null
  roster: LtiRosterEntry[]
  student: LtiStudent | null
  enrollments: LtiEnrollment[]
}
