import { render, screen } from '@testing-library/react'

import { Button } from '@/components/ui/Button'

describe('Button', () => {
  it('renders the primary variant label', () => {
    render(<Button variant="primary">Save draft</Button>)

    expect(
      screen.getByRole('button', {
        name: 'Save draft',
      }),
    ).toBeInTheDocument()
  })

  it('shows a spinner and disables interaction while loading', () => {
    render(
      <Button variant="secondary" loading>
        Sign in
      </Button>,
    )

    expect(screen.getByRole('button')).toBeDisabled()
    expect(screen.getByLabelText('Loading')).toBeInTheDocument()
  })
})
