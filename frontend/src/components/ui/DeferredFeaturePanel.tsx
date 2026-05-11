import type { ReactNode } from 'react'

import { Card, CardTitle } from '@/components/ui/Card'

export function DeferredFeaturePanel({
  children,
  phaseLabel,
  title,
}: {
  children: ReactNode
  phaseLabel: string
  title: string
}) {
  return (
    <Card className="border-dashed border-neutral-300 bg-neutral-50">
      <p className="font-mono text-xs uppercase tracking-[0.16em] text-neutral-500">{phaseLabel}</p>
      <CardTitle className="mt-2">{title}</CardTitle>
      <div className="mt-3 text-sm text-neutral-600">{children}</div>
    </Card>
  )
}
