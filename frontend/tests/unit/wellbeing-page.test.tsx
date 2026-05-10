import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { StudentWellbeingPage } from '@/pages/student/Wellbeing'
import * as useWellbeing from '@/hooks/useWellbeing'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'

vi.mock('@/hooks/useWellbeing')

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    <MemoryRouter>
      {children}
    </MemoryRouter>
  </QueryClientProvider>
)

describe('StudentWellbeingPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders consent page when not enabled', async () => {
    vi.mocked(useWellbeing.useWellbeingConsent).mockReturnValue({ data: { is_enabled: false }, isLoading: false } as any)
    vi.mocked(useWellbeing.useWellbeingHistory).mockReturnValue({ data: [], isLoading: false } as any)
    vi.mocked(useWellbeing.useUpdateWellbeingConsent).mockReturnValue({ mutate: vi.fn(), isPending: false } as any)

    render(<StudentWellbeingPage />, { wrapper })

    expect(screen.getByText(/Enable Wellbeing Check-In/i)).toBeInTheDocument()
  })

  it('renders check-in form when consented', async () => {
    vi.mocked(useWellbeing.useWellbeingConsent).mockReturnValue({ data: { is_enabled: true }, isLoading: false } as any)
    vi.mocked(useWellbeing.useWellbeingHistory).mockReturnValue({ data: [], isLoading: false } as any)
    vi.mocked(useWellbeing.useWellbeingTriage).mockReturnValue({ mutate: vi.fn(), isPending: false } as any)

    render(<StudentWellbeingPage />, { wrapper })

    expect(screen.getByText(/How are you feeling today?/i)).toBeInTheDocument()
  })
})
