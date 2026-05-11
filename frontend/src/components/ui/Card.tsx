import type { HTMLAttributes, ReactNode } from 'react'

import { cn } from '@/utils/cn'

type Accent = 'danger' | 'warning' | 'success' | 'info'

const accentClasses: Record<Accent, string> = {
  danger: 'border-l-4 border-l-danger bg-red-50',
  warning: 'border-l-4 border-l-warning bg-amber-50',
  success: 'border-l-4 border-l-success bg-green-50',
  info: 'border-l-4 border-l-info bg-sky-50',
}

export function Card({
  accent,
  children,
  className,
  interactive = false,
  ...props
}: HTMLAttributes<HTMLDivElement> & {
  accent?: Accent
  interactive?: boolean
}) {
  return (
    <div
      className={cn(
        'rounded-card border border-neutral-200 bg-white p-6 shadow-card',
        interactive && 'transition-shadow duration-150 hover:shadow-card-hover',
        accent && accentClasses[accent],
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardTitle({ children, className }: { children: ReactNode; className?: string }) {
  return <h3 className={cn('text-base font-semibold text-neutral-900', className)}>{children}</h3>
}
