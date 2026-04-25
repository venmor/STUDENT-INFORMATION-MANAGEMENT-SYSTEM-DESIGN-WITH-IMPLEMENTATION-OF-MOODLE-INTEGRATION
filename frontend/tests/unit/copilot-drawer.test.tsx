import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { CopilotDrawer } from '@/components/ai/CopilotDrawer'

describe('CopilotDrawer', () => {
  it('renders the disclaimer, loading skeleton, and source citation', async () => {
    const user = userEvent.setup()

    render(<CopilotDrawer />)

    await user.click(screen.getByRole('button', { name: 'Ask Co-pilot' }))

    expect(screen.getByText(/Responses are AI-generated/i)).toBeInTheDocument()
    expect(screen.getByLabelText('Copilot loading')).toBeInTheDocument()
    expect(screen.getByText('Source: Deferred until Phase 4 AI build')).toBeInTheDocument()
    expect(screen.getByText(/Please verify with the Registrar/i)).toBeInTheDocument()
  })
})
