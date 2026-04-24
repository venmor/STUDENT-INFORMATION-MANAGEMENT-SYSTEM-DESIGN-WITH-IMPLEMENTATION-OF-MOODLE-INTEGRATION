import type { FormEvent } from 'react'
import { startTransition, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { roleHomePath } from '@/app/role-home'
import { useAuth } from '@/auth/auth-context'

export function LoginPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const { loginUser } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')
    setIsSubmitting(true)

    try {
      const session = await loginUser({ username, password })
      const requestedPath = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname
      startTransition(() => {
        navigate(requestedPath ?? roleHomePath(session.user.primaryRole), { replace: true })
      })
    } catch {
      setErrorMessage('The username or password is incorrect.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-8">
      <div className="grid w-full max-w-6xl gap-6 rounded-[2.25rem] border border-white/60 bg-white/75 p-5 shadow-[0_28px_110px_rgba(15,23,42,0.16)] backdrop-blur lg:grid-cols-[1.15fr_0.85fr] lg:p-8">
        <section className="rounded-[2rem] bg-[linear-gradient(160deg,rgba(15,23,42,0.96),rgba(15,118,110,0.9))] px-6 py-8 text-white lg:px-8">
          <p className="text-xs uppercase tracking-[0.32em] text-orange-200">Phase 2 Step 2.4</p>
          <h1 className="mt-4 text-4xl font-semibold leading-tight sm:text-5xl">Modern SIS access</h1>
          <p className="mt-4 max-w-xl text-sm text-slate-100 sm:text-base">
            The first role-aware frontend for student records, registration, advising, grades, and user
            administration. Phase 3 and AI surfaces are marked clearly where the backend contract is not available yet.
          </p>
        </section>

        <section className="rounded-[2rem] border border-slate-200 bg-[#fffaf2] px-6 py-8">
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="username">
                Username
              </label>
              <input
                id="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="min-h-12 w-full rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
                required
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="min-h-12 w-full rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
                required
              />
            </div>

            {errorMessage ? (
              <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {errorMessage}
              </div>
            ) : null}

            <button
              type="submit"
              disabled={isSubmitting}
              className="min-h-12 w-full rounded-2xl bg-slate-900 px-5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </button>
          </form>
        </section>
      </div>
    </div>
  )
}

export default LoginPage
