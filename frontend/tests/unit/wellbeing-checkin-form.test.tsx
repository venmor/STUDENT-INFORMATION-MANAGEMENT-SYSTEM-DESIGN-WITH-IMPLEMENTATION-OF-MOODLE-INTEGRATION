import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { WellbeingCheckInForm } from '@/components/wellbeing/WellbeingCheckInForm'
import * as useWellbeing from '@/hooks/useWellbeing'
import { QueryClient, QueryClientProvider, type UseQueryResult, type UseMutationResult } from '@tanstack/react-query'
import type { WellbeingConsent, WellbeingCheckIn } from '@/api/wellbeing'

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
    {children}
  </QueryClientProvider>
)

describe('WellbeingCheckInForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('keeps submit disabled until a mood is selected', async () => {
    vi.mocked(useWellbeing.useWellbeingConsent).mockReturnValue({ data: { is_enabled: true }, isLoading: false } as UseQueryResult<WellbeingConsent>)
    vi.mocked(useWellbeing.useWellbeingTriage).mockReturnValue({ mutate: vi.fn(), isPending: false } as unknown as UseMutationResult<WellbeingCheckIn, Error, { mood_rating: number; comment?: string }>)

    const user = userEvent.setup()

    render(<WellbeingCheckInForm />, { wrapper })

    const submitButton = screen.getByRole('button', { name: 'Submit check-in' })
    expect(submitButton).toBeDisabled()

    // Our new MoodSelector uses aria-label on the emoji span, button itself might not have the text.
    // Let's find by role button and check aria-label or just use the emoji.
    await user.click(screen.getByLabelText('Okay'))

    expect(submitButton).toBeEnabled()
  })
})
