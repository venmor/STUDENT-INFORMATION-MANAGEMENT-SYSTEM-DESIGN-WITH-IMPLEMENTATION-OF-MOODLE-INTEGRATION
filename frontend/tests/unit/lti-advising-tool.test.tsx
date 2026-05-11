import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { AdvisingToolPage } from '@/pages/lti/AdvisingTool'
import type { LtiSessionContext } from '@/types/lti'

const context: LtiSessionContext = {
  tool: 'advising-dashboard',
  isMapped: true,
  launch: {
    issuer: 'https://moodle.example.test',
    clientId: 'client-123',
    deploymentId: 'deployment-456',
    moodleSubject: 'moodle-sub-42',
    moodleUserId: '42',
    moodleCourseId: '77',
    roles: ['Instructor'],
    context: { id: '77', label: 'CSC101', title: 'Intro CS' },
    resourceLink: { id: 'resource-1', title: 'Advising dashboard' },
    targetLinkUri: '/lti/tools/advising-dashboard',
  },
  sisUser: {
    id: '1',
    username: 'advisor.one',
    fullName: 'Advisor One',
    email: 'advisor.one@example.com',
    primaryRole: 'ADVISOR',
  },
  section: {
    id: '11',
    courseCode: 'CSC101',
    courseTitle: 'Intro CS',
    sectionCode: 'A1',
    semester: 'Semester 1',
    academicYear: '2026/2027',
    faculty: 'Faculty One',
    capacity: 40,
  },
  roster: [
    {
      studentId: '101',
      studentNumber: '2026/CS/001',
      fullName: 'Asha Phiri',
      email: 'asha@example.com',
      enrollmentStatus: 'ENROLLED',
      engagement: null,
    },
    {
      studentId: '102',
      studentNumber: '2026/CS/002',
      fullName: 'Mina Banda',
      email: 'mina@example.com',
      enrollmentStatus: 'ENROLLED',
      engagement: {
        collectedAt: '2026-04-30T09:00:00Z',
        moodleLastAccessAt: '2026-04-29T08:00:00Z',
        moodleCourseLastAccessAt: '2026-04-30T07:30:00Z',
        assignmentSubmissionCount: null,
        assignmentSubmissionRate: null,
        quizAttemptCount: null,
        quizAverage: null,
        forumPostCount: null,
      },
    },
  ],
  student: null,
  enrollments: [],
}

describe('AdvisingToolPage', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => context,
      }),
    )
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('lets advisors select a roster student and inspect Moodle engagement context', async () => {
    render(<AdvisingToolPage />)

    expect(
      await screen.findByRole('heading', { name: 'Advising dashboard' }),
    ).toBeInTheDocument()
    await userEvent.click(
      screen.getByRole('button', { name: 'Select Mina Banda' }),
    )

    expect(
      screen.getByRole('heading', { name: 'Selected student' }),
    ).toBeInTheDocument()
    expect(screen.getAllByText('Mina Banda').length).toBeGreaterThan(0)
    expect(screen.getByText('Moodle engagement')).toBeInTheDocument()
    expect(screen.getByText('Course last access')).toBeInTheDocument()
    expect(screen.getAllByText(/2026/).length).toBeGreaterThan(0)
  })
})
