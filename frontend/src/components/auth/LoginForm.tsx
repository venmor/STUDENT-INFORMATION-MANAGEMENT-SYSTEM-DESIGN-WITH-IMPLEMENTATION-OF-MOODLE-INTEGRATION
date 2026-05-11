import { useState } from 'react'
import { EyeIcon, EyeSlashIcon, LockClosedIcon } from '@heroicons/react/24/outline'
import { useNavigate } from 'react-router-dom'

import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useAuth } from '@/hooks/useAuth'
import { roleHomePath } from '@/utils/roleGuards'

export function LoginForm() {
  const navigate = useNavigate()
  const { signIn } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const response = await signIn(username, password)
      navigate(roleHomePath(response.user.primary_role), { replace: true })
    } catch {
      setError('Sign-in failed. Verify your username and password and try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form className="space-y-5" onSubmit={handleSubmit}>
      {error ? (
        <Alert tone="danger" title="Unable to sign in">
          {error}
        </Alert>
      ) : null}
      <Input
        id="username"
        label="Username"
        placeholder="Enter your username"
        value={username}
        onChange={(event) => setUsername(event.target.value)}
      />
      <div className="space-y-1.5">
        <label htmlFor="password" className="block text-sm font-medium text-neutral-700">
          Password
        </label>
        <div className="relative">
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            className="block w-full rounded-lg border border-neutral-300 px-4 py-2.5 pr-12 text-neutral-900 placeholder:text-neutral-400 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            placeholder="Enter your password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <button
            type="button"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            className="absolute inset-y-0 right-0 flex min-h-11 min-w-11 items-center justify-center text-neutral-500"
            onClick={() => setShowPassword((value) => !value)}
          >
            {showPassword ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
          </button>
        </div>
      </div>
      <Button type="submit" variant="primary" size="lg" loading={isSubmitting} className="w-full">
        Sign in
      </Button>
      <div className="flex items-center gap-2 text-xs text-neutral-500">
        <LockClosedIcon className="h-4 w-4" />
        <span>Role access is enforced after sign-in. Contact the registrar for account issues.</span>
      </div>
    </form>
  )
}
