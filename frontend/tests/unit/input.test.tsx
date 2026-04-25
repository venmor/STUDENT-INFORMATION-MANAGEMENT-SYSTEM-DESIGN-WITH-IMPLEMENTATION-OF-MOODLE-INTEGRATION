import { render, screen } from '@testing-library/react'

import { Input } from '@/components/ui/Input'

describe('Input', () => {
  it('connects the label to the input', () => {
    render(<Input id="student-number" label="Student number" />)

    expect(screen.getByLabelText('Student number')).toHaveAttribute('id', 'student-number')
  })

  it('renders an error state and announces the error text', () => {
    render(<Input id="username" label="Username" error="Username is required." />)

    const input = screen.getByLabelText('Username')
    const error = screen.getByRole('alert')

    expect(error).toHaveTextContent('Username is required.')
    expect(input).toHaveAttribute('aria-describedby', 'username-error')
  })
})
