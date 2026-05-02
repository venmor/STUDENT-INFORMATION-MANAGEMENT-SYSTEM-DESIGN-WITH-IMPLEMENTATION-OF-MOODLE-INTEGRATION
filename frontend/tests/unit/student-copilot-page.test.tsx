import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'

import { StudentCopilotPage } from '@/pages/student/Copilot'

const apiMocks = vi.hoisted(() => ({
  getCopilotSessions: vi.fn(),
  createCopilotSession: vi.fn(),
  getCopilotSession: vi.fn(),
  archiveCopilotSession: vi.fn(),
  queryCopilot: vi.fn(),
  rateCopilotMessage: vi.fn(),
}))

vi.mock('@/api/copilot', () => apiMocks)

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason?: unknown) => void
  const promise = new Promise<T>((res, rej) => {
    resolve = res
    reject = rej
  })
  return { promise, resolve, reject }
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <StudentCopilotPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

const successfulAnswer = {
  sessionId: 'session-1',
  messageId: 'message-1',
  answer:
    'The drop deadline is listed in the Academic Calendar. After the deadline, verify options with the Registrar office.',
  confidence: 'LOW',
  sources: [
    {
      sourceId: 'source-1',
      chunkId: 'chunk-1',
      title: 'Academic Calendar Deadline Guide',
      sourceType: 'ACADEMIC_CALENDAR',
      preview: 'The deadline to drop a course is the published drop deadline in the academic calendar.',
      score: 0.82,
    },
  ],
  suggestedNextActions: [
    { label: 'Open Academic Calendar', url: '/calendar' },
    { label: 'Open Registration', url: '/student/register' },
  ],
  disclaimer: 'Please verify this with the Registrar office if your case is unusual.',
}

describe('student co-pilot page', () => {
  beforeEach(() => {
    apiMocks.getCopilotSessions.mockResolvedValue([])
    apiMocks.createCopilotSession.mockResolvedValue({ id: 'session-new', title: 'New chat', status: 'ACTIVE' })
    apiMocks.getCopilotSession.mockResolvedValue(null)
    apiMocks.archiveCopilotSession.mockResolvedValue(null)
    apiMocks.queryCopilot.mockReset()
    apiMocks.rateCopilotMessage.mockResolvedValue(null)
  })

  it('renders examples, accessible composer, safety notice, and no emoji text', () => {
    const { container } = renderPage()

    expect(screen.getByText('Responses are generated from institutional sources and your safe student context.')).toBeInTheDocument()
    expect(screen.getByText('What is the deadline to drop a course?')).toBeInTheDocument()
    expect(screen.getByText('How do I register for courses?')).toBeInTheDocument()
    expect(screen.getByLabelText('Ask the AI co-pilot')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
    expect(container.textContent).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u)
  })

  it('submits a question, shows thinking state, and renders answer details', async () => {
    const user = userEvent.setup()
    const pending = deferred<typeof successfulAnswer>()
    apiMocks.queryCopilot.mockReturnValueOnce(pending.promise)

    renderPage()

    await user.type(screen.getByLabelText('Ask the AI co-pilot'), 'What is the deadline to drop a course?')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(screen.getByText('What is the deadline to drop a course?')).toBeInTheDocument()
    expect(screen.getByText('Searching institutional sources...')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()

    pending.resolve(successfulAnswer)

    expect(await screen.findByText(/The drop deadline is listed in the Academic Calendar/i)).toBeInTheDocument()
    expect(screen.getByText('Confidence: LOW')).toBeInTheDocument()
    expect(screen.getAllByText('Academic Calendar Deadline Guide')).toHaveLength(2)
    expect(screen.getByText('Relevance 0.82')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Open Academic Calendar' })).toHaveAttribute('href', '/calendar')
    expect(screen.getByRole('link', { name: 'Open Registration' })).toHaveAttribute('href', '/student/register')
    expect(screen.getByText(/Please verify this with the Registrar office/i)).toBeInTheDocument()
  })

  it('shows an error with retry when the request fails', async () => {
    const user = userEvent.setup()
    apiMocks.queryCopilot.mockRejectedValueOnce(new Error('Network failed'))
    apiMocks.queryCopilot.mockResolvedValueOnce(successfulAnswer)

    renderPage()

    await user.type(screen.getByLabelText('Ask the AI co-pilot'), 'How do I register for courses?')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(await screen.findByText('The co-pilot could not answer that question.')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Try again' }))

    await waitFor(() => expect(apiMocks.queryCopilot).toHaveBeenCalledTimes(2))
    expect(await screen.findByText(/The drop deadline is listed/i)).toBeInTheDocument()
  })
})
