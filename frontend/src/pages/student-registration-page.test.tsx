import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, expect, it, vi } from 'vitest'

import { AuthProvider } from '@/auth/auth-context'
import { StudentRegistrationPage } from '@/pages/student-registration-page'

vi.mock('@/api/academics', () => ({
  createEnrollment: vi.fn().mockResolvedValue({ id: 'enr-1' }),
  dropEnrollment: vi.fn().mockResolvedValue({ id: 'enr-1' }),
  getEnrollments: vi.fn().mockResolvedValue([]),
  getSections: vi.fn().mockResolvedValue([
    {
      id: 'section-1',
      course_id: 'course-1',
      course_code: 'CSC201',
      course_title: 'Algorithms',
      section_code: 'A',
      faculty_user_id: 4,
      faculty_full_name: 'Dr Faculty',
      room: 'Lab 2',
      semester: 'Semester 1',
      academic_year: '2026/2027',
      max_capacity: 30,
      registration_opens_at: '2026-04-01T00:00:00Z',
      registration_closes_at: '2026-05-15T23:59:59Z',
      drop_deadline: '2026-05-20T23:59:59Z',
      status: 'ACTIVE',
      current_enrollment_count: 12,
      timetables: [],
    },
  ]),
}))

import { createEnrollment } from '@/api/academics'

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider
        initialSession={{
          accessToken: 'token',
          refreshToken: 'refresh',
          expiresAt: Date.now() + 60_000,
          user: {
            id: 2,
            username: 'student1',
            fullName: 'Student One',
            primaryRole: 'STUDENT',
            mustResetPassword: false,
            studentProfileId: 'student-1',
          },
        }}
      >
        <StudentRegistrationPage />
      </AuthProvider>
    </QueryClientProvider>,
  )
}

describe('Student registration page', () => {
  it('submits an enrollment request for an available section', async () => {
    renderPage()

    expect(await screen.findByText(/algorithms/i)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /enroll/i }))

    await waitFor(() => {
      expect(createEnrollment).toHaveBeenCalled()
      expect(vi.mocked(createEnrollment).mock.calls[0]?.[0]).toEqual({
        sectionId: 'section-1',
        waitlistIfFull: false,
      })
    })
  })
})
