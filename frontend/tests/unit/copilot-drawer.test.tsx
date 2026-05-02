import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { CopilotDrawer } from '@/components/ai/CopilotDrawer'

describe('CopilotDrawer', () => {
  it('links to the implemented student co-pilot route', () => {
    render(
      <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
        <CopilotDrawer />
      </MemoryRouter>,
    )

    expect(screen.getByRole('link', { name: 'Open AI Co-pilot' })).toHaveAttribute('href', '/student/copilot')
    expect(screen.getByText('AI Co-pilot')).toBeInTheDocument()
  })
})
