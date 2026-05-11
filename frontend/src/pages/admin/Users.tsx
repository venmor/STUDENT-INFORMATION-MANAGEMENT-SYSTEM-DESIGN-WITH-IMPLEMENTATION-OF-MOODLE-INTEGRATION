import { useState } from 'react'

import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { EnhancedDataTable, type Column } from '@/components/ui/EnhancedDataTable'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { useUserMutations, useUsers } from '@/hooks/useUsers'
import { useToast } from '@/hooks/useToast'
import type { UserSummary } from '@/types'

const userColumns: Column<UserSummary>[] = [
  { key: 'username', label: 'Username', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  {
    key: 'primary_role',
    label: 'Role',
    sortable: true,
    filterable: true,
    filterOptions: [
      { label: 'Student', value: 'STUDENT' },
      { label: 'Advisor', value: 'ADVISOR' },
      { label: 'Faculty', value: 'FACULTY' },
      { label: 'Admin', value: 'ADMIN' },
    ],
  },
]

export function AdminUsersPage() {
  const { data: users = [] } = useUsers()
  const mutations = useUserMutations()
  const { addToast } = useToast()
  const [form, setForm] = useState({
    username: '',
    email: '',
    fullName: '',
    primaryRole: 'STUDENT',
    temporaryPassword: '',
  })

  return (
    <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <Card>
        <CardTitle>Create user</CardTitle>
        <div className="mt-4 space-y-4">
          <Input id="create-username" label="Username" value={form.username} onChange={(event) => setForm((state) => ({ ...state, username: event.target.value }))} />
          <Input id="create-email" label="Email" value={form.email} onChange={(event) => setForm((state) => ({ ...state, email: event.target.value }))} />
          <Input id="create-full-name" label="Full name" value={form.fullName} onChange={(event) => setForm((state) => ({ ...state, fullName: event.target.value }))} />
          <Select
            id="create-role"
            label="Primary role"
            value={form.primaryRole}
            onValueChange={(primaryRole) => setForm((state) => ({ ...state, primaryRole }))}
            items={[
              { value: 'STUDENT', label: 'Student' },
              { value: 'ADVISOR', label: 'Advisor' },
              { value: 'FACULTY', label: 'Faculty' },
              { value: 'ADMIN', label: 'Admin' },
            ]}
          />
          <Input id="create-password" label="Temporary password" value={form.temporaryPassword} onChange={(event) => setForm((state) => ({ ...state, temporaryPassword: event.target.value }))} />
          <Button
            loading={mutations.createUser.isPending}
            onClick={() =>
              mutations.createUser.mutate(form, {
                onSuccess: () => {
                  addToast('User created', `${form.username} has been created successfully.`, 'success')
                  setForm({ username: '', email: '', fullName: '', primaryRole: 'STUDENT', temporaryPassword: '' })
                },
                onError: (err) => addToast('Failed to create user', String(err.message), 'error'),
              })
            }
          >
            Create user
          </Button>
        </div>
      </Card>
      <Card>
        <CardTitle>User directory</CardTitle>
        <div className="mt-4">
          <EnhancedDataTable
            data={users}
            columns={userColumns}
            ariaLabel="User directory"
            searchableKeys={['username', 'email']}
            actions={(user) => (
              <div className="flex flex-wrap gap-2">
                <Button variant="secondary" size="sm" onClick={() => mutations.resetUserPassword.mutate({ userId: user.id, newPassword: 'TempPass123!' })}>
                  Reset password
                </Button>
                <Button variant="ghost" size="sm" onClick={() => mutations.deactivateUser.mutate(user.id)}>
                  Deactivate
                </Button>
              </div>
            )}
          />
        </div>
      </Card>
    </div>
  )
}
