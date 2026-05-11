import type { ReactNode } from 'react'

import { Card } from '@/components/ui/Card'

export function SystemHealthCard({
  detail,
  icon,
  label,
  status,
}: {
  detail: string
  icon: ReactNode
  label: string
  status: string
}) {
  return (
    <Card className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="text-primary">{icon}</div>
        <span className="font-mono text-xs text-neutral-500">{status}</span>
      </div>
      <div>
        <p className="text-sm font-medium text-neutral-700">{label}</p>
        <p className="mt-1 text-sm text-neutral-500">{detail}</p>
      </div>
    </Card>
  )
}
