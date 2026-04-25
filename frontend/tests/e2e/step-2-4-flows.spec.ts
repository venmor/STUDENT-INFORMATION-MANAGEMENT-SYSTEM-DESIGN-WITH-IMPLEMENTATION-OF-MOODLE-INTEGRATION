import { expect, test, type Page, type Route } from '@playwright/test'

type PrimaryRole = 'STUDENT' | 'ADVISOR' | 'FACULTY' | 'ADMIN'

const studentProfile = {
  id: 'student-1',
  user_id: 201,
  username: 'student.one',
  full_name: 'Temba Mwansa',
  email: 'temba@example.edu',
  student_number: '2026/CS/001',
  national_id: '111111/11/1',
  date_of_birth: '2003-02-14',
  gender: 'M',
  programme: 'BSc Computer Science',
  year_of_study: 4,
  academic_standing: 'GOOD',
  cumulative_gpa: '3.42',
  standing_override_reason: '',
  is_active: true,
  attendance_flags: [],
  attendance_percentages: [
    {
      section_id: 'section-1',
      course_code: 'CSC410',
      attendance_percentage: '87',
      threshold: '75',
    },
  ],
}

const section = {
  id: 'section-1',
  course_id: 'course-1',
  course_code: 'CSC410',
  course_title: 'Distributed Systems',
  section_code: 'A1',
  faculty_user_id: 401,
  faculty_full_name: 'Dr. Ncube',
  room: 'LT-4',
  semester: 'Semester 1',
  academic_year: '2026/2027',
  max_capacity: 80,
  registration_opens_at: '2026-04-01T08:00:00Z',
  registration_closes_at: '2026-04-30T17:00:00Z',
  drop_deadline: '2026-05-07T17:00:00Z',
  attendance_threshold: '75',
  status: 'OPEN',
  timetables: [
    {
      id: 'tt-1',
      day_of_week: 'MONDAY',
      start_time: '08:00:00',
      end_time: '10:00:00',
    },
  ],
  current_enrollment_count: 1,
}

const roster = [
  {
    id: 'roster-1',
    student_id: 'student-1',
    user_id: 201,
    student_number: '2026/CS/001',
    full_name: 'Temba Mwansa',
    email: 'temba@example.edu',
    programme: 'BSc Computer Science',
    year_of_study: 4,
    enrollment_status: 'ENROLLED',
  },
]

const notes = [
  {
    id: 'note-1',
    note_text: 'Needs follow-up on project milestones.',
    status: 'DRAFT',
    created_by_username: 'advisor.one',
    approved_by_username: null,
    approved_at: null,
    created_at: '2026-04-10T08:00:00Z',
    updated_at: '2026-04-10T08:00:00Z',
  },
]

const flags = [
  {
    id: 'flag-1',
    flag_type: 'BALANCE',
    reason: 'Outstanding balance',
    effective_date: '2026-04-05',
    cleared_date: null,
    created_at: '2026-04-05T08:00:00Z',
  },
]

const grades = [
  {
    id: 'grade-1',
    student_id: 'student-1',
    student_number: '2026/CS/001',
    section_id: 'section-1',
    course_code: 'CSC410',
    course_title: 'Distributed Systems',
    section_code: 'A1',
    numeric_score: '84',
    letter_grade: 'A',
    grade_points: '4.0',
    grade_status: 'OFFICIAL',
    special_code: '',
    entered_at: '2026-04-08T08:00:00Z',
    officialised_at: '2026-04-12T08:00:00Z',
  },
]

const initialUsers = [
  {
    id: 1,
    username: 'admin.one',
    email: 'admin@example.edu',
    full_name: 'Admin One',
    primary_role: 'ADMIN',
    is_active: true,
    must_reset_password: false,
    capability_names: [],
  },
]

function json(route: Route, payload: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(payload),
  })
}

function authPayload(role: PrimaryRole) {
  return {
    access_token: `access-${role.toLowerCase()}`,
    refresh_token: `refresh-${role.toLowerCase()}`,
    expires_in: 900,
    user: {
      id: role === 'STUDENT' ? 201 : role === 'ADVISOR' ? 301 : role === 'FACULTY' ? 401 : 1,
      username: `${role.toLowerCase()}.one`,
      full_name:
        role === 'STUDENT'
          ? 'Temba Mwansa'
          : role === 'ADVISOR'
            ? 'Advisor One'
            : role === 'FACULTY'
              ? 'Dr. Ncube'
              : 'Admin One',
      primary_role: role,
      must_reset_password: false,
      student_profile_id: role === 'STUDENT' ? studentProfile.id : null,
    },
  }
}

async function installApiMocks(page: Page, role: PrimaryRole) {
  let enrollments: Array<Record<string, unknown>> =
    role === 'STUDENT'
      ? [
          {
            id: 'enrollment-1',
            student_id: studentProfile.id,
            section_id: section.id,
            enrollment_status: 'ENROLLED',
            is_active: true,
            reason: '',
            enrolled_at: '2026-04-04T08:00:00Z',
            dropped_at: null,
            section,
          },
        ]
      : []

  let users = [...initialUsers]
  const capturedGradeBodies: Array<Record<string, unknown>> = []

  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const path = url.pathname.replace('/api/v1', '')

    if (path === '/auth/login' && request.method() === 'POST') {
      return json(route, authPayload(role))
    }

    if (path === '/auth/refresh' && request.method() === 'POST') {
      return json(route, {
        access_token: `refreshed-${role.toLowerCase()}`,
        refresh_token: `refresh-${role.toLowerCase()}`,
        expires_in: 900,
      })
    }

    if (path === '/students' && request.method() === 'GET') {
      return json(route, role === 'ADVISOR' || role === 'ADMIN' ? [studentProfile] : [])
    }

    if (path === `/students/${studentProfile.id}` && request.method() === 'GET') {
      return json(route, studentProfile)
    }

    if (path === `/students/${studentProfile.id}/financial-flags` && request.method() === 'GET') {
      return json(route, flags)
    }

    if (path === `/students/${studentProfile.id}/advising-notes` && request.method() === 'GET') {
      return json(route, notes)
    }

    if (path === `/students/${studentProfile.id}/correction-requests` && request.method() === 'GET') {
      return json(route, [])
    }

    if (path === '/sections' && request.method() === 'GET') {
      return json(route, [section])
    }

    if (path === `/sections/${section.id}` && request.method() === 'GET') {
      return json(route, section)
    }

    if (path === `/sections/${section.id}/roster` && request.method() === 'GET') {
      return json(route, roster)
    }

    if (path === '/enrollments' && request.method() === 'GET') {
      return json(route, enrollments)
    }

    if (path === '/enrollments' && request.method() === 'POST') {
      const body = request.postDataJSON() as { section_id: string }
      const newEnrollment = {
        id: `enrollment-${enrollments.length + 1}`,
        student_id: studentProfile.id,
        section_id: body.section_id,
        enrollment_status: 'ENROLLED',
        is_active: true,
        reason: '',
        enrolled_at: '2026-04-25T08:00:00Z',
        dropped_at: null,
        section,
      }
      enrollments = [...enrollments, newEnrollment]
      return json(route, newEnrollment, 201)
    }

    if (path.endsWith('/drop') && request.method() === 'POST') {
      const enrollmentId = path.split('/')[2]
      enrollments = enrollments.filter((entry) => entry.id !== enrollmentId)
      return json(route, { ok: true })
    }

    if (path === '/grades' && request.method() === 'GET') {
      return json(route, grades)
    }

    if (path === '/grades' && request.method() === 'POST') {
      capturedGradeBodies.push(request.postDataJSON() as Record<string, unknown>)
      return json(route, {
        ...grades[0],
        id: `grade-${capturedGradeBodies.length + 1}`,
        numeric_score: String((request.postDataJSON() as { numeric_score: string }).numeric_score ?? ''),
        grade_status: 'DRAFT',
        officialised_at: null,
      }, 201)
    }

    if (path === '/users' && request.method() === 'GET') {
      return json(route, users)
    }

    if (path === '/users' && request.method() === 'POST') {
      const body = request.postDataJSON() as {
        email: string
        full_name: string
        primary_role: PrimaryRole
        username: string
      }
      const newUser = {
        id: users.length + 1,
        username: body.username,
        email: body.email,
        full_name: body.full_name,
        primary_role: body.primary_role,
        is_active: true,
        must_reset_password: true,
        capability_names: [],
      }
      users = [...users, newUser]
      return json(route, newUser, 201)
    }

    if (path.endsWith('/reset-password') || path.endsWith('/deactivate') || path === '/users/change-password') {
      return json(route, { ok: true })
    }

    return json(route, { detail: `Unhandled mock route for ${request.method()} ${path}` }, 404)
  })

  return {
    capturedGradeBodies,
  }
}

async function login(page: Page, role: PrimaryRole) {
  await page.goto('/login')
  await page.getByLabel('Username').fill(`${role.toLowerCase()}.one`)
  await page.locator('#password').fill('Password123!')
  await page.getByRole('button', { name: 'Sign in' }).click()
}

test.describe('Phase 2 Step 2.4 frontend rebuild', () => {
  for (const role of ['STUDENT', 'ADVISOR', 'FACULTY', 'ADMIN'] as const) {
    test(`redirects ${role.toLowerCase()} users to the correct dashboard`, async ({ page }) => {
      await installApiMocks(page, role)
      await login(page, role)

      await expect(page).toHaveURL(new RegExp(`/${role.toLowerCase()}$`))
    })
  }

  test('student registration updates the current registration list', async ({ page }) => {
    await installApiMocks(page, 'STUDENT')
    await login(page, 'STUDENT')
    await page.goto('/student/register')

    const dropButtons = page.getByRole('button', { name: 'Drop' })
    const dropButtonsBefore = await dropButtons.count()
    await page.getByLabel('Select a section').click()
    await page.getByRole('option', { name: 'CSC410 · A1 · Dr. Ncube' }).click()
    await page.getByRole('button', { name: 'Register for selected section' }).click()

    await expect(dropButtons).toHaveCount(dropButtonsBefore + 1)
  })

  test('advisor can search and open a unified student profile', async ({ page }) => {
    await installApiMocks(page, 'ADVISOR')
    await login(page, 'ADVISOR')

    await page.getByPlaceholder('Search by student name or student number').fill('Temba')
    await page.getByRole('link', { name: /Temba Mwansa/i }).click()

    await expect(page).toHaveURL(/\/advisor\/students\/student-1$/)
    await expect(page.getByRole('heading', { name: 'Temba Mwansa' })).toBeVisible()
    await expect(page.getByRole('tab', { name: 'Academic Record' })).toBeVisible()
  })

  test('faculty can submit a draft grade entry', async ({ page }) => {
    const mocks = await installApiMocks(page, 'FACULTY')
    await login(page, 'FACULTY')

    await page.getByRole('link', { name: /Distributed Systems/i }).click()
    await page.getByLabel('Student user ID').fill('201')
    await page.getByLabel('Score').fill('78')
    await page.getByRole('button', { name: 'Save draft grade' }).click()

    await expect.poll(() => mocks.capturedGradeBodies.length).toBe(1)
    expect(mocks.capturedGradeBodies[0]).toMatchObject({
      student_user_id: 201,
      section_id: 'section-1',
      numeric_score: '78',
    })
  })

  test('admin can create a new user from the user administration page', async ({ page }) => {
    await installApiMocks(page, 'ADMIN')
    await login(page, 'ADMIN')

    await page.goto('/admin/users')
    await page.getByLabel('Username').fill('faculty.two')
    await page.getByLabel('Email').fill('faculty.two@example.edu')
    await page.getByLabel('Full name').fill('Faculty Two')
    await page.getByLabel('Primary role').click()
    await page.getByRole('option', { name: 'Faculty' }).click()
    await page.getByLabel('Temporary password').fill('TempPass123!')
    await page.getByRole('button', { name: 'Create user' }).click()

    await expect(page.getByRole('cell', { name: 'faculty.two', exact: true })).toBeVisible()
  })

  test('student wellbeing shell exposes quick-exit and privacy-first copy', async ({ page }) => {
    await installApiMocks(page, 'STUDENT')
    await login(page, 'STUDENT')

    await page.goto('/student/wellbeing')

    await expect(page.getByRole('link', { name: 'Quick Exit' })).toHaveAttribute('href', 'https://www.example.edu')
    await expect(page.getByRole('heading', { name: 'Wellbeing Check-In' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Submit check-in' })).toBeDisabled()
  })
})
