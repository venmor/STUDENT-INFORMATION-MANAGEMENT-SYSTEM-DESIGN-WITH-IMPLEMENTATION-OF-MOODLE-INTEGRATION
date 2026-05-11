import type { ReactNode } from 'react'

import { cn } from '@/utils/cn'

const tones = {
  default: 'border border-neutral-200 bg-neutral-100 text-neutral-700',
  success: 'border border-success/20 bg-success/10 text-success',
  warning: 'border border-warning/20 bg-warning/10 text-warning',
  danger: 'border border-danger/20 bg-danger/10 text-danger',
  dangerSolid: 'bg-danger text-white',
  info: 'border border-info/20 bg-info/10 text-info',
} as const

export function Badge({
  children,
  className,
  tone = 'default',
}: {
  children: ReactNode
  className?: string
  tone?: keyof typeof tones
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  )
}
