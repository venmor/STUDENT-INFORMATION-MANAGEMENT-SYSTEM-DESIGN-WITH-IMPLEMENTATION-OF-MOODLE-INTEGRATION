import { useState } from 'react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'

export function InlineGradeEntry({
  onSubmit,
}: {
  onSubmit: (payload: { numericScore: string; studentUserId: number }) => void
}) {
  const [studentUserId, setStudentUserId] = useState('')
  const [numericScore, setNumericScore] = useState('')

  return (
    <div className="space-y-4">
      <Input
        id="student-user-id"
        label="Student user ID"
        placeholder="Numeric user ID"
        value={studentUserId}
        onChange={(event) => setStudentUserId(event.target.value)}
      />
      <Input
        id="numeric-score"
        label="Score"
        placeholder="0 - 100"
        value={numericScore}
        onChange={(event) => setNumericScore(event.target.value)}
      />
      <Button onClick={() => onSubmit({ numericScore, studentUserId: Number(studentUserId) })}>Save draft grade</Button>
    </div>
  )
}
