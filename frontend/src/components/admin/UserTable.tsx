import { Button } from '@/components/ui/Button'
import { DataTable, DataTableBody, DataTableCell, DataTableHead, DataTableHeader, DataTableRow } from '@/components/ui/Table'
import type { UserSummary } from '@/types'

export function UserTable({
  onDeactivate,
  onResetPassword,
  users,
}: {
  onDeactivate: (userId: number) => void
  onResetPassword: (userId: number) => void
  users: UserSummary[]
}) {
  return (
    <DataTable ariaLabel="User table">
      <DataTableHead>
        <tr>
          <DataTableHeader>Username</DataTableHeader>
          <DataTableHeader>Role</DataTableHeader>
          <DataTableHeader>Email</DataTableHeader>
          <DataTableHeader>Actions</DataTableHeader>
        </tr>
      </DataTableHead>
      <DataTableBody>
        {users.map((user) => (
          <DataTableRow key={user.id}>
            <DataTableCell>{user.username}</DataTableCell>
            <DataTableCell className="font-mono">{user.primary_role}</DataTableCell>
            <DataTableCell>{user.email}</DataTableCell>
            <DataTableCell>
              <div className="flex flex-wrap gap-2">
                <Button variant="secondary" size="sm" onClick={() => onResetPassword(user.id)}>
                  Reset password
                </Button>
                <Button variant="ghost" size="sm" onClick={() => onDeactivate(user.id)}>
                  Deactivate
                </Button>
              </div>
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}
