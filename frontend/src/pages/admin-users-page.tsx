import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { createUser, deactivateUser, getUsers, resetUserPassword } from '@/api/users'
import { DataState } from '@/components/ui/data-state'
import { PageHeader } from '@/components/ui/page-header'
import { Panel } from '@/components/ui/panel'

export default function AdminUsersPage() {
  const queryClient = useQueryClient()
  const [formState, setFormState] = useState({
    username: '',
    email: '',
    fullName: '',
    primaryRole: 'STUDENT',
    temporaryPassword: '',
  })
  const [message, setMessage] = useState('')

  const usersQuery = useQuery({
    queryKey: ['users', 'admin-users'],
    queryFn: getUsers,
  })

  const createUserMutation = useMutation({
    mutationFn: createUser,
    onSuccess: async () => {
      setFormState({
        username: '',
        email: '',
        fullName: '',
        primaryRole: 'STUDENT',
        temporaryPassword: '',
      })
      setMessage('User created.')
      await queryClient.invalidateQueries({ queryKey: ['users'] })
    },
    onError: () => {
      setMessage('User creation failed.')
    },
  })

  const deactivateMutation = useMutation({
    mutationFn: deactivateUser,
    onSuccess: async () => {
      setMessage('User deactivated.')
      await queryClient.invalidateQueries({ queryKey: ['users'] })
    },
  })

  const resetMutation = useMutation({
    mutationFn: ({ userId }: { userId: number }) => resetUserPassword(userId, 'Reset123!'),
    onSuccess: () => {
      setMessage('Password reset to Reset123! and marked for mandatory change.')
    },
  })

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Admin users"
        title="User management"
        description="Create accounts, deactivate users, and force password resets from the verified admin surface."
      />

      <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <Panel title="Create user" description="New accounts are created with a temporary password and a required reset flag.">
          <form
            className="grid gap-4"
            onSubmit={(event) => {
              event.preventDefault()
              setMessage('')
              createUserMutation.mutate({
                ...formState,
                capabilityNames: [],
              })
            }}
          >
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Username</span>
              <input
                value={formState.username}
                onChange={(event) => setFormState((current) => ({ ...current, username: event.target.value }))}
                className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
                required
              />
            </label>
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Email</span>
              <input
                type="email"
                value={formState.email}
                onChange={(event) => setFormState((current) => ({ ...current, email: event.target.value }))}
                className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
                required
              />
            </label>
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Full name</span>
              <input
                value={formState.fullName}
                onChange={(event) => setFormState((current) => ({ ...current, fullName: event.target.value }))}
                className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
                required
              />
            </label>
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Primary role</span>
              <select
                value={formState.primaryRole}
                onChange={(event) => setFormState((current) => ({ ...current, primaryRole: event.target.value }))}
                className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
              >
                <option value="STUDENT">STUDENT</option>
                <option value="ADVISOR">ADVISOR</option>
                <option value="FACULTY">FACULTY</option>
                <option value="ADMIN">ADMIN</option>
              </select>
            </label>
            <label className="grid gap-2 text-sm text-slate-700">
              <span>Temporary password</span>
              <input
                type="password"
                value={formState.temporaryPassword}
                onChange={(event) =>
                  setFormState((current) => ({ ...current, temporaryPassword: event.target.value }))
                }
                className="min-h-11 rounded-2xl border border-slate-300 bg-white px-4 outline-none transition focus:border-slate-900"
                required
              />
            </label>
            {message ? <p className="text-sm text-slate-700">{message}</p> : null}
            <button
              type="submit"
              disabled={createUserMutation.isPending}
              className="min-h-11 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {createUserMutation.isPending ? 'Creating...' : 'Create user'}
            </button>
          </form>
        </Panel>

        <Panel title="Current users" description="Deactivation and password reset actions are available inline for each user.">
          {usersQuery.isLoading ? (
            <DataState title="Loading users" message="Fetching user accounts." />
          ) : usersQuery.isError ? (
            <DataState title="User load failed" message="User accounts could not be loaded." />
          ) : usersQuery.data && usersQuery.data.length ? (
            <div className="space-y-3">
              {usersQuery.data.map((user) => (
                <article key={user.id} className="rounded-[1.5rem] border border-slate-200 bg-[#fffdfa] p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-lg font-semibold text-slate-900">{user.full_name}</p>
                      <p className="mt-1 text-sm text-slate-600">
                        {user.username} · {user.primary_role}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={() => resetMutation.mutate({ userId: user.id })}
                        className="min-h-11 rounded-2xl border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700"
                      >
                        Reset password
                      </button>
                      {user.is_active ? (
                        <button
                          type="button"
                          onClick={() => deactivateMutation.mutate(user.id)}
                          className="min-h-11 rounded-2xl border border-red-300 bg-red-50 px-4 py-2 text-sm font-semibold text-red-700"
                        >
                          Deactivate
                        </button>
                      ) : null}
                    </div>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <DataState title="No users" message="No users are present yet." />
          )}
        </Panel>
      </div>
    </div>
  )
}
