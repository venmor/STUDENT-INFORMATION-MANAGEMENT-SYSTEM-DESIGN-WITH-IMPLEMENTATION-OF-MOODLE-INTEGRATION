import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { AdminAIFoundationPage } from '@/pages/admin/AIFoundation'

const mocks = vi.hoisted(() => ({
  testQueryMutate: vi.fn(),
  state: {} as Record<string, unknown>,
}))

vi.mock('@/hooks/useAIFoundation', () => ({
  useAnalyticsSummary: () => mocks.state.analyticsSummary,
  useAnalyticsSnapshots: () => mocks.state.analyticsSnapshots,
  useAnalyticsRuns: () => mocks.state.analyticsRuns,
  useKnowledgeSummary: () => mocks.state.knowledgeSummary,
  useKnowledgeSources: () => mocks.state.knowledgeSources,
  useKnowledgeIngestionRuns: () => mocks.state.knowledgeRuns,
  useKnowledgeTestQuery: () => ({
    mutate: mocks.testQueryMutate,
    isPending: false,
    data: mocks.state.queryResult,
  }),
}))

function queryResult(data: unknown, overrides: Record<string, unknown> = {}) {
  return {
    data,
    isLoading: false,
    isError: false,
    refetch: vi.fn(),
    ...overrides,
  }
}

function setDefaultHookState(overrides: Record<string, unknown> = {}) {
  mocks.state = {
    analyticsSummary: queryResult({
      latestRun: {
        id: 'etl-1',
        status: 'SUCCEEDED',
        startedAt: '2026-05-01T10:00:00Z',
        completedAt: '2026-05-01T10:01:00Z',
      },
      studentsWithSnapshots: 2,
      moodleSnapshotsUsed: 3,
      averageAttendance: '82.50',
      officialGradeCount: 4,
      financialFlags: 1,
      latestMoodleAccessAt: '2026-05-01T09:00:00Z',
    }),
    analyticsSnapshots: queryResult([
      {
        id: 'snapshot-1',
        student: {
          id: 'student-1',
          studentNumber: '2026/CS/001',
          fullName: 'Temba Mwansa',
          programme: 'BSc Computer Science',
        },
        academicYear: '2026/2027',
        semester: 'Semester 1',
        attendanceAverage: '82.50',
        activeEnrollmentCount: 2,
        officialGradeCount: 1,
        financialFlagCount: 1,
        moodleSnapshotCount: 2,
        updatedAt: '2026-05-01T10:01:00Z',
      },
    ]),
    analyticsRuns: queryResult([
      {
        id: 'etl-1',
        status: 'SUCCEEDED',
        studentsProcessed: 2,
        snapshotsCreated: 2,
        snapshotsUpdated: 0,
        moodleSnapshotsUsed: 3,
        failureCount: 0,
        dryRun: false,
        startedAt: '2026-05-01T10:00:00Z',
        completedAt: '2026-05-01T10:01:00Z',
      },
    ]),
    knowledgeSummary: queryResult({
      sources: 5,
      chunks: 12,
      latestIngestion: {
        id: 'ingestion-1',
        status: 'SUCCEEDED',
        chunksUpserted: 12,
        completedAt: '2026-05-01T10:02:00Z',
      },
      vectorStore: {
        provider: 'memory',
        collection: 'modern_sis_knowledge',
        healthy: true,
        message: 'Ready',
      },
    }),
    knowledgeSources: queryResult([
      {
        id: 'source-1',
        title: 'Academic Calendar Deadline Guide',
        sourceType: 'ACADEMIC_CALENDAR',
        visibility: 'PUBLIC_STUDENT',
        status: 'INGESTED',
        chunkCount: 4,
        updatedAt: '2026-05-01T10:00:00Z',
      },
    ]),
    knowledgeRuns: queryResult([
      {
        id: 'ingestion-1',
        status: 'SUCCEEDED',
        sourcesProcessed: 5,
        chunksCreated: 12,
        chunksUpserted: 12,
        failureCount: 0,
        startedAt: '2026-05-01T10:01:00Z',
        completedAt: '2026-05-01T10:02:00Z',
      },
    ]),
    queryResult: {
      query: 'What is the deadline to drop a course?',
      generatedAnswer: null,
      results: [
        {
          chunkId: 'chunk-1',
          sourceId: 'source-1',
          sourceTitle: 'Academic Calendar Deadline Guide',
          sourceType: 'ACADEMIC_CALENDAR',
          score: 0.91,
          text: 'Students must drop a course before the published drop deadline in the academic calendar.',
        },
      ],
    },
    ...overrides,
  }
}

function renderPage() {
  return render(
    <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
      <AdminAIFoundationPage />
    </MemoryRouter>,
  )
}

describe('AI foundation admin page', () => {
  beforeEach(() => {
    mocks.testQueryMutate.mockClear()
    setDefaultHookState()
  })

  it('renders analytics readiness, knowledge state, retrieval test, scope note, and no emoji text', () => {
    const { container } = renderPage()

    expect(screen.getByText('Latest ETL Run')).toBeInTheDocument()
    expect(screen.getByText('Student Snapshots')).toBeInTheDocument()
    expect(screen.getByText('Vector Store')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Analytics Readiness' })).toBeInTheDocument()
    expect(screen.getByText('Temba Mwansa')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Knowledge Base' })).toBeInTheDocument()
    expect(screen.getAllByText('Academic Calendar Deadline Guide')).toHaveLength(2)
    expect(screen.getByLabelText('Test retrieval query')).toBeInTheDocument()
    expect(screen.getByText('This page tests retrieval only. It does not call an LLM or generate student-facing AI answers.')).toBeInTheDocument()
    expect(container.textContent).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u)
  })

  it('runs retrieval test and displays source chunk results', () => {
    renderPage()

    fireEvent.change(screen.getByLabelText('Test retrieval query'), {
      target: { value: 'What is the deadline to drop a course?' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Run Retrieval Test' }))

    expect(mocks.testQueryMutate).toHaveBeenCalledWith({ query: 'What is the deadline to drop a course?', limit: 5 })
    expect(screen.getByText('Score 0.91')).toBeInTheDocument()
    expect(screen.getByText(/Students must drop a course before the published drop deadline/i)).toBeInTheDocument()
  })

  it('renders loading, empty, and error states', () => {
    setDefaultHookState({
      analyticsSummary: queryResult(undefined, { isLoading: true }),
      knowledgeSummary: queryResult(undefined, { isError: true }),
      knowledgeSources: queryResult([]),
    })

    renderPage()

    expect(screen.getByText('Loading AI foundation summary')).toBeInTheDocument()
    expect(screen.getByText('Could not load knowledge foundation status')).toBeInTheDocument()
    expect(screen.getByText('No knowledge sources found')).toBeInTheDocument()
  })
})
