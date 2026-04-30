import { Navigate, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { AppShell } from '@/components/layout/AppShell'
import { useCurrentUser } from '@/hooks/useCurrentUser'
import { AccessDeniedPage } from '@/pages/AccessDenied'
import { AccountPasswordPage } from '@/pages/AccountPassword'
import { LoginPage } from '@/pages/Login'
import { NotFoundPage } from '@/pages/NotFound'
import { AdminAuditLogPage } from '@/pages/admin/AuditLog'
import { AdminCoursesPage } from '@/pages/admin/Courses'
import { AdminDashboardPage } from '@/pages/admin/Dashboard'
import { AdminMoodleSyncPage } from '@/pages/admin/MoodleSync'
import { AdminUsersPage } from '@/pages/admin/Users'
import { AdvisorAlertHistoryPage } from '@/pages/advisor/AlertHistory'
import { AdvisorDashboardPage } from '@/pages/advisor/Dashboard'
import { AdvisorStudentProfilePage } from '@/pages/advisor/StudentProfile'
import { FacultyDashboardPage } from '@/pages/faculty/Dashboard'
import { FacultySectionDetailPage } from '@/pages/faculty/SectionDetail'
import { AdvisingToolPage } from '@/pages/lti/AdvisingTool'
import { RegistrationToolPage } from '@/pages/lti/RegistrationTool'
import { StudentCorrectionsPage } from '@/pages/student/Corrections'
import { StudentCourseRegistrationPage } from '@/pages/student/CourseRegistration'
import { StudentDashboardPage } from '@/pages/student/Dashboard'
import { StudentGradesPage } from '@/pages/student/MyGrades'
import { StudentCoursesPage } from '@/pages/student/MyCourses'
import { StudentWellbeingPage } from '@/pages/student/Wellbeing'

function HomeRedirect() {
  const user = useCurrentUser()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <Navigate to={`/${user.primaryRole.toLowerCase()}`} replace />
}

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forbidden" element={<AccessDeniedPage />} />
      <Route path="/lti/tools/advising-dashboard" element={<AdvisingToolPage />} />
      <Route path="/lti/tools/registration" element={<RegistrationToolPage />} />

      <Route element={<ProtectedRoute allowedRoles={['STUDENT', 'ADVISOR', 'FACULTY', 'ADMIN']} />}>
        <Route element={<AppShell />}>
          <Route path="/account/password" element={<AccountPasswordPage />} />

          <Route element={<ProtectedRoute allowedRoles={['STUDENT']} />}>
            <Route path="/student" element={<StudentDashboardPage />} />
            <Route path="/student/courses" element={<StudentCoursesPage />} />
            <Route path="/student/grades" element={<StudentGradesPage />} />
            <Route path="/student/register" element={<StudentCourseRegistrationPage />} />
            <Route path="/student/corrections" element={<StudentCorrectionsPage />} />
            <Route path="/student/wellbeing" element={<StudentWellbeingPage />} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['ADVISOR']} />}>
            <Route path="/advisor" element={<AdvisorDashboardPage />} />
            <Route path="/advisor/students/:studentId" element={<AdvisorStudentProfilePage />} />
            <Route path="/advisor/alerts" element={<AdvisorAlertHistoryPage />} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['FACULTY']} />}>
            <Route path="/faculty" element={<FacultyDashboardPage />} />
            <Route path="/faculty/sections/:sectionId" element={<FacultySectionDetailPage />} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
            <Route path="/admin" element={<AdminDashboardPage />} />
            <Route path="/admin/users" element={<AdminUsersPage />} />
            <Route path="/admin/courses" element={<AdminCoursesPage />} />
            <Route path="/admin/moodle-sync" element={<AdminMoodleSyncPage />} />
            <Route path="/admin/audit-log" element={<AdminAuditLogPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
