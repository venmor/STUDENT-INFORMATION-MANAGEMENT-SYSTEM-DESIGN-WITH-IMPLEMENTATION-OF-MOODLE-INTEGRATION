import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { StudentWellbeingPage } from '@/pages/student/Wellbeing'
import * as useWellbeing from '@/hooks/useWellbeing'
import { QueryClient, QueryClientProvider, type UseQueryResult, type UseMutationResult } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import type { WellbeingConsent, WellbeingHistoryItem, WellbeingCheckIn } from '@/api/wellbeing'

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
    vi.mocked(useWellbeing.useWellbeingConsent).mockReturnValue({ data: { is_enabled: false }, isLoading: false } as UseQueryResult<WellbeingConsent>)
    vi.mocked(useWellbeing.useWellbeingHistory).mockReturnValue({ data: [], isLoading: false } as UseQueryResult<WellbeingHistoryItem[]>)
    vi.mocked(useWellbeing.useUpdateWellbeingConsent).mockReturnValue({ mutate: vi.fn(), isPending: false } as unknown as UseMutationResult<WellbeingConsent, Error, boolean>)

    render(<StudentWellbeingPage />, { wrapper })

    expect(screen.getByText(/Enable Wellbeing Check-In/i)).toBeInTheDocument()
  })

  it('renders check-in form when consented', async () => {
    vi.mocked(useWellbeing.useWellbeingConsent).mockReturnValue({ data: { is_enabled: true }, isLoading: false } as UseQueryResult<WellbeingConsent>)
    vi.mocked(useWellbeing.useWellbeingHistory).mockReturnValue({ data: [], isLoading: false } as UseQueryResult<WellbeingHistoryItem[]>)
    vi.mocked(useWellbeing.useWellbeingTriage).mockReturnValue({ mutate: vi.fn(), isPending: false } as unknown as UseMutationResult<WellbeingCheckIn, Error, { mood_rating: number; comment?: string }>)

    render(<StudentWellbeingPage />, { wrapper })

    expect(screen.getByText(/How are you feeling today?/i)).toBeInTheDocument()
  })
})
