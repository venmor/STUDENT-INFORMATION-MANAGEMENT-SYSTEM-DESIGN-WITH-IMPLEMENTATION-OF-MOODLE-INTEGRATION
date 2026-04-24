export type PrimaryRole = 'STUDENT' | 'ADVISOR' | 'FACULTY' | 'ADMIN'

export interface LoginPayload {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  expires_in: number
  user: {
    id: number
    username: string
    full_name: string
    primary_role: PrimaryRole
    must_reset_password: boolean
    student_profile_id: string | null
  }
}

export interface RefreshResponse {
  access_token: string
  refresh_token: string
  expires_in: number
}

export interface UserSummary {
  id: number
  username: string
  email: string
  full_name: string
  primary_role: PrimaryRole
  is_active: boolean
  must_reset_password: boolean
  capability_names: string[]
}

export interface StudentAttendanceSummary {
  section_id: string
  course_code: string
  attendance_percentage: string
  threshold: string
}

export interface StudentProfile {
  id: string
  user_id: number
  username: string
  full_name: string
  email: string
  student_number: string
  national_id: string
  date_of_birth: string
  gender: string
  programme: string
  year_of_study: number
  academic_standing: string
  cumulative_gpa: string
  standing_override_reason: string
  is_active: boolean
  attendance_flags: StudentAttendanceSummary[]
  attendance_percentages: StudentAttendanceSummary[]
}

export interface FinancialFlag {
  id: string
  flag_type: string
  reason: string
  effective_date: string
  cleared_date: string | null
  created_at: string
}

export interface AdvisingNote {
  id: string
  note_text: string
  status: string
  created_by_username: string
  approved_by_username: string | null
  approved_at: string | null
  created_at: string
  updated_at: string
}

export interface StudentCorrectionRequest {
  id: string
  requested_changes: string
  justification: string
  status: string
  review_note: string
  reviewed_by_username: string | null
  reviewed_at: string | null
  created_at: string
  updated_at: string
}

export interface SectionTimetable {
  id: string
  day_of_week: string
  start_time: string
  end_time: string
}

export interface Course {
  id: string
  course_code: string
  course_title: string
  department: string
  credit_hours: number
  description: string
  programme_code: string
  max_capacity: number
  is_active: boolean
}

export interface CourseSection {
  id: string
  course_id: string
  course_code: string
  course_title: string
  section_code: string
  faculty_user_id: number
  faculty_full_name: string
  room: string
  semester: string
  academic_year: string
  max_capacity: number
  registration_opens_at: string
  registration_closes_at: string
  drop_deadline: string
  attendance_threshold: string
  status: string
  timetables: SectionTimetable[]
  current_enrollment_count: number
}

export interface Enrollment {
  id: string
  student_id: string
  section_id: string
  enrollment_status: string
  is_active: boolean
  reason: string
  enrolled_at: string
  dropped_at: string | null
  section: CourseSection
}

export interface GradeRecord {
  id: string
  student_id: string
  student_number: string
  section_id: string
  course_code: string
  course_title: string
  section_code: string
  numeric_score: string | null
  letter_grade: string
  grade_points: string
  grade_status: string
  special_code: string
  entered_at: string
  officialised_at: string | null
}

export interface SectionRosterEntry {
  id: string
  student_id: string
  user_id: number
  student_number: string
  full_name: string
  email: string
  programme: string
  year_of_study: number
  enrollment_status: string
}
