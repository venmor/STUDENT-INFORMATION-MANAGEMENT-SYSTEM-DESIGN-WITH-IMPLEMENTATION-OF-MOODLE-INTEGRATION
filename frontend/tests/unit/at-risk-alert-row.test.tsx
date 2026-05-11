import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { AtRiskAlertRow } from '@/components/advisor/AtRiskAlertRow'

describe('AtRiskAlertRow', () => {
  it('renders HIGH severity with danger styling', () => {
    const { container } = render(
      <AtRiskAlertRow
        severity="HIGH"
        studentName="Temba Mwansa"
        timestamp="2026-04-10 02:14"
        explanation="Attendance and quiz performance both dropped this week."
      />,
    )

    expect(screen.getByText('HIGH — Temba Mwansa')).toBeInTheDocument()
    expect(container.firstChild).toHaveClass('bg-red-50', 'border-l-danger')
  })

  it('renders MEDIUM severity with warning styling', () => {
    const { container } = render(
      <AtRiskAlertRow
        severity="MEDIUM"
        studentName="Mwila Chanda"
        timestamp="2026-04-10 08:00"
        explanation="The GPA trend requires advisor review."
      />,
    )

    expect(screen.getByText('MEDIUM — Mwila Chanda')).toBeInTheDocument()
    expect(container.firstChild).toHaveClass('bg-amber-50', 'border-l-warning')
  })

  it('calls the acknowledge handler', async () => {
    const user = userEvent.setup()
    const handleAcknowledge = vi.fn()

    render(
      <AtRiskAlertRow
        severity="LOW"
        studentName="Chipo Lungu"
        timestamp="2026-04-10 11:42"
        explanation="Low-severity signal set for follow-up."
        onAcknowledge={handleAcknowledge}
      />,
    )

    await user.click(screen.getByRole('button', { name: 'Acknowledge' }))

    expect(handleAcknowledge).toHaveBeenCalledTimes(1)
  })
})
