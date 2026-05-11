import { useState } from 'react'

import { changePassword } from '@/api/users'
import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'

export function AccountPasswordPage() {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit() {
    setError(null)
    setMessage(null)
    setIsSubmitting(true)
    try {
      await changePassword({ currentPassword, newPassword })
      setMessage('Password updated successfully.')
      setCurrentPassword('')
      setNewPassword('')
    } catch {
      setError('Password update failed. Check your current password and try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-xl">
      <Card>
        <CardTitle>Change password</CardTitle>
        <div className="mt-4 space-y-4">
          {message ? <Alert tone="success">{message}</Alert> : null}
          {error ? <Alert tone="danger">{error}</Alert> : null}
          <Input id="current-password" label="Current password" type="password" value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} />
          <Input id="new-password" label="New password" type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} />
          <Button loading={isSubmitting} onClick={handleSubmit}>
            Update password
          </Button>
        </div>
      </Card>
    </div>
  )
}
