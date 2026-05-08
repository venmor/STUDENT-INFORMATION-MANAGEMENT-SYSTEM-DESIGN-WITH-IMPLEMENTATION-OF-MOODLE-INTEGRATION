import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { SummarisationForm } from '@/features/summarisation/SummarisationForm'

describe('SummarisationForm', () => {
  it('renders governance notice', () => {
    render(<SummarisationForm onSubmit={vi.fn()} isPending={false} />)
    expect(screen.getByText(/AI-generated summaries must be reviewed/)).toBeInTheDocument()
  })

  it('renders character counter', () => {
    render(<SummarisationForm onSubmit={vi.fn()} isPending={false} />)
    expect(screen.getByText('0 / 5000')).toBeInTheDocument()
  })

  it('disables button when input is empty', () => {
    render(<SummarisationForm onSubmit={vi.fn()} isPending={false} />)
    expect(screen.getByRole('button', { name: /generate summary/i })).toBeDisabled()
  })

  it('calls onSubmit with text when button clicked', async () => {
    const onSubmit = vi.fn()
    render(<SummarisationForm onSubmit={onSubmit} isPending={false} />)
    const textarea = screen.getByLabelText(/raw advising notes/i)
    await userEvent.type(textarea, 'Student missed three classes.')
    await userEvent.click(screen.getByRole('button', { name: /generate summary/i }))
    expect(onSubmit).toHaveBeenCalledWith('Student missed three classes.')
  })

  it('shows truncation warning when over limit', () => {
    render(<SummarisationForm onSubmit={vi.fn()} isPending={false} />)
    const textarea = screen.getByLabelText(/raw advising notes/i)
    fireEvent.change(textarea, { target: { value: 'x'.repeat(5001) } })
    expect(screen.getByText(/exceeds the 5000 character limit/)).toBeInTheDocument()
  })
})
