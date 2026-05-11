import { useState } from 'react'

import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { UserTable } from '@/components/admin/UserTable'
import { useUserMutations, useUsers } from '@/hooks/useUsers'

export function AdminUsersPage() {
  const { data: users = [] } = useUsers()
  const mutations = useUserMutations()
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
            onClick={() => mutations.createUser.mutate(form)}
          >
            Create user
          </Button>
        </div>
      </Card>
      <Card>
        <CardTitle>User directory</CardTitle>
        <div className="mt-4">
          <UserTable
            users={users}
            onDeactivate={(userId) => mutations.deactivateUser.mutate(userId)}
            onResetPassword={(userId) => mutations.resetUserPassword.mutate({ userId, newPassword: 'TempPass123!' })}
          />
        </div>
      </Card>
    </div>
  )
}
