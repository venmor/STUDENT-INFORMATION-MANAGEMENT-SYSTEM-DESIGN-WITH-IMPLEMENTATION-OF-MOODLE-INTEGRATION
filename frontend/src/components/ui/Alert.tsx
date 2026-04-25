import type { ReactNode } from 'react'

import { XMarkIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'
import { cn } from '@/utils/cn'

const tones = {
  info: 'border-sky-200 bg-sky-50 text-sky-900',
  success: 'border-green-200 bg-green-50 text-green-900',
  warning: 'border-amber-200 bg-amber-50 text-amber-900',
  danger: 'border-red-200 bg-red-50 text-red-900',
} as const

export function Alert({
  action,
  children,
  className,
  dismissLabel = 'Dismiss alert',
  icon,
  onDismiss,
  tone = 'info',
  title,
}: {
  action?: ReactNode
  children: ReactNode
  className?: string
  dismissLabel?: string
  icon?: ReactNode
  onDismiss?: () => void
  tone?: keyof typeof tones
  title?: string
}) {
  return (
    <div className={cn('rounded-lg border px-4 py-3', tones[tone], className)} role="alert">
      <div className="flex items-start gap-3">
        {icon ? <div className="mt-0.5 flex-shrink-0">{icon}</div> : null}
        <div className="min-w-0 flex-1">
          {title ? <h4 className="text-sm font-semibold">{title}</h4> : null}
          <div className="text-sm">{children}</div>
          {action ? <div className="mt-3">{action}</div> : null}
        </div>
        {onDismiss ? (
          <Button
            variant="ghost"
            size="sm"
            className="min-w-0 px-2 text-current"
            aria-label={dismissLabel}
            onClick={onDismiss}
          >
            <XMarkIcon className="h-4 w-4" />
          </Button>
        ) : null}
      </div>
    </div>
  )
}
