import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { WellbeingCheckInForm } from '@/components/wellbeing/WellbeingCheckInForm'

describe('WellbeingCheckInForm', () => {
  it('keeps submit disabled until a mood is selected', async () => {
    const user = userEvent.setup()

    render(<WellbeingCheckInForm />)

    const submitButton = screen.getByRole('button', { name: 'Submit check-in' })
    expect(submitButton).toBeDisabled()

    await user.click(screen.getByRole('button', { name: '3 — Okay' }))

    expect(submitButton).toBeEnabled()
  })
})
