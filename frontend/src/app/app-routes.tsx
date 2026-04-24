import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { AuthenticatedRoute } from '@/app/authenticated-route'
import { AppShell } from '@/components/layout/app-shell'
import { RoleRoute } from '@/app/role-route'
import { roleHomePath } from '@/app/role-home'
import { useAuth } from '@/auth/auth-context'
import { DataState } from '@/components/ui/data-state'
import { ForbiddenPage } from '@/pages/forbidden-page'

const LoginPage = lazy(() => import('@/pages/login-page'))
const StudentOverviewPage = lazy(() => import('@/pages/student-overview-page'))
const StudentGradesPage = lazy(() => import('@/pages/student-grades-page'))
const StudentRegistrationPage = lazy(() => import('@/pages/student-registration-page'))
const StudentCorrectionsPage = lazy(() => import('@/pages/student-corrections-page'))
const AdvisorOverviewPage = lazy(() => import('@/pages/advisor-overview-page'))
const AdvisorStudentPage = lazy(() => import('@/pages/advisor-student-page'))
const FacultyOverviewPage = lazy(() => import('@/pages/faculty-overview-page'))
const FacultySectionPage = lazy(() => import('@/pages/faculty-section-page'))
const AdminOverviewPage = lazy(() => import('@/pages/admin-overview-page'))
const AdminUsersPage = lazy(() => import('@/pages/admin-users-page'))
const AdminStudentPage = lazy(() => import('@/pages/admin-student-page'))
const AccountPasswordPage = lazy(() => import('@/pages/account-password-page'))
const NotFoundPage = lazy(() => import('@/pages/not-found-page'))

function RouteFallback() {
  return <DataState title="Loading route" message="Preparing the requested screen." />
}

function AppIndexRedirect() {
  const { session } = useAuth()

  if (!session) {
    return <Navigate to="/login" replace />
  }

  return <Navigate to={roleHomePath(session.user.primaryRole)} replace />
}

export function AppRoutes() {
  return (
    <Suspense fallback={<RouteFallback />}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forbidden" element={<ForbiddenPage />} />
        <Route path="/" element={<AppIndexRedirect />} />

        <Route element={<AuthenticatedRoute />}>
          <Route element={<AppShell />}>
            <Route path="/account/password" element={<AccountPasswordPage />} />

            <Route element={<RoleRoute allowedRoles={['STUDENT']} />}>
              <Route path="/student/overview" element={<StudentOverviewPage />} />
              <Route path="/student/grades" element={<StudentGradesPage />} />
              <Route path="/student/registration" element={<StudentRegistrationPage />} />
              <Route path="/student/corrections" element={<StudentCorrectionsPage />} />
            </Route>

            <Route element={<RoleRoute allowedRoles={['ADVISOR']} />}>
              <Route path="/advisor/overview" element={<AdvisorOverviewPage />} />
              <Route path="/advisor/students/:studentId" element={<AdvisorStudentPage />} />
            </Route>

            <Route element={<RoleRoute allowedRoles={['FACULTY']} />}>
              <Route path="/faculty/overview" element={<FacultyOverviewPage />} />
              <Route path="/faculty/sections/:sectionId" element={<FacultySectionPage />} />
            </Route>

            <Route element={<RoleRoute allowedRoles={['ADMIN']} />}>
              <Route path="/admin/overview" element={<AdminOverviewPage />} />
              <Route path="/admin/users" element={<AdminUsersPage />} />
              <Route path="/admin/students/:studentId" element={<AdminStudentPage />} />
            </Route>
          </Route>
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  )
}
