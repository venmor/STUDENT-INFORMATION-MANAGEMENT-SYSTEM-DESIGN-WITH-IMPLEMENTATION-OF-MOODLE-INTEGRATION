import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { SummarisationResult } from '@/features/summarisation/SummarisationResult'

describe('SummarisationResult', () => {
  const defaultProps = {
    keyIssues: ['Issue one', 'Issue two'],
    recommendedActions: ['Action one'],
    urgencyLevel: 'Routine',
    onApprove: vi.fn(),
    onDiscard: vi.fn(),
    isApproving: false,
  }

  it('renders editable issues', () => {
    render(<SummarisationResult {...defaultProps} />)
    expect(screen.getByDisplayValue('Issue one')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Issue two')).toBeInTheDocument()
  })

  it('renders urgency selector with correct value', () => {
    render(<SummarisationResult {...defaultProps} />)
    const select = screen.getByRole('combobox')
    expect(select).toHaveValue('Routine')
  })

  it('calls onApprove with edited data', async () => {
    const onApprove = vi.fn()
    render(<SummarisationResult {...defaultProps} onApprove={onApprove} />)
    await userEvent.click(screen.getByRole('button', { name: /approve and save/i }))
    expect(onApprove).toHaveBeenCalledWith({
      key_issues: ['Issue one', 'Issue two'],
      recommended_actions: ['Action one'],
      urgency_level: 'Routine',
    })
  })

  it('calls onDiscard when discard clicked', async () => {
    const onDiscard = vi.fn()
    render(<SummarisationResult {...defaultProps} onDiscard={onDiscard} />)
    await userEvent.click(screen.getByRole('button', { name: /discard/i }))
    expect(onDiscard).toHaveBeenCalled()
  })

  it('renders add item buttons', () => {
    render(<SummarisationResult {...defaultProps} />)
    const addButtons = screen.getAllByText(/\+ add item/i)
    expect(addButtons.length).toBeGreaterThan(0)
  })

  it('disables approve button when no non-empty issues', () => {
    render(<SummarisationResult {...defaultProps} keyIssues={['']} recommendedActions={['Do something']} />)
    expect(screen.getByRole('button', { name: /approve and save/i })).toBeDisabled()
  })
})
