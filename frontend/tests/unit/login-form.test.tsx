import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import { LoginForm } from '@/components/auth/LoginForm'

const navigate = vi.fn()
const signIn = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom')
  return {
    ...actual,
    useNavigate: () => navigate,
  }
})

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    signIn,
  }),
}))

describe('LoginForm', () => {
  beforeEach(() => {
    navigate.mockReset()
    signIn.mockReset()
  })

  it('shows an error alert on failed sign-in', async () => {
    signIn.mockRejectedValueOnce(new Error('bad credentials'))

    render(<LoginForm />)

    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'student.one' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'incorrect-password' } })
    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }))

    expect(await screen.findByText('Unable to sign in')).toBeInTheDocument()
    expect(screen.getByText(/Verify your username and password/i)).toBeInTheDocument()
  })

  it('disables the submit button while sign-in is in flight', async () => {
    let resolveSignIn: ((value: unknown) => void) | undefined
    signIn.mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          resolveSignIn = resolve
        }),
    )

    render(<LoginForm />)

    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'student.one' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'correct-password' } })
    fireEvent.click(screen.getByRole('button', { name: 'Sign in' }))

    expect(screen.getByRole('button', { name: 'Loading' })).toBeDisabled()

    resolveSignIn?.({
      user: {
        primary_role: 'STUDENT',
      },
    })

    await waitFor(() => {
      expect(navigate).toHaveBeenCalledWith('/student', { replace: true })
    })
  })
})
