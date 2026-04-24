import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'

import { changePassword } from '@/api/auth'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'

export default function AccountPasswordPage() {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [message, setMessage] = useState('')

  const mutation = useMutation({
    mutationFn: changePassword,
    onSuccess: () => {
      setMessage('Password updated.')
      setCurrentPassword('')
      setNewPassword('')
    },
    onError: () => {
      setMessage('Password update failed. Check the current password and policy.')
    },
  })

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Account security"
        title="Change password"
        description="This screen is available to every authenticated role and calls the shared password-change endpoint."
      />
      <Panel title="Password change" description="The backend enforces current-password verification and the configured password policy.">
        <form
          className="grid gap-4 md:max-w-xl"
          onSubmit={(event) => {
            event.preventDefault()
            mutation.mutate({ currentPassword, newPassword })
          }}
        >
          <label className="grid gap-2 text-sm text-slate-700">
            <span>Current password</span>
            <input
              type="password"
              value={currentPassword}
              onChange={(event) => setCurrentPassword(event.target.value)}
              className="min-h-12 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
              required
            />
          </label>
          <label className="grid gap-2 text-sm text-slate-700">
            <span>New password</span>
            <input
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              className="min-h-12 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
              required
            />
          </label>
          {message ? <p className="text-sm text-slate-700">{message}</p> : null}
          <button
            type="submit"
            disabled={mutation.isPending}
            className="min-h-12 rounded-2xl bg-slate-900 px-5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {mutation.isPending ? 'Updating...' : 'Update password'}
          </button>
        </form>
      </Panel>
    </div>
  )
}
