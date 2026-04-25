import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { cn } from '@/utils/cn'

const severityStyles = {
  HIGH: 'border-l-danger bg-red-50 text-danger',
  MEDIUM: 'border-l-warning bg-amber-50 text-warning',
  LOW: 'border-l-info bg-sky-50 text-info',
} as const

export function AtRiskAlertRow({
  acknowledged = false,
  explanation,
  onAcknowledge,
  severity,
  studentName,
  timestamp,
}: {
  acknowledged?: boolean
  explanation: string
  onAcknowledge?: () => void
  severity: keyof typeof severityStyles
  studentName: string
  timestamp: string
}) {
  return (
    <div className={cn('flex items-start gap-4 rounded-r-lg border-l-4 p-4', severityStyles[severity], acknowledged && 'opacity-60')}>
      <ExclamationTriangleIcon className="mt-0.5 h-5 w-5 flex-shrink-0" />
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <h4 className="text-sm font-semibold">
            {severity} — {studentName}
          </h4>
          <span className="font-mono text-xs text-neutral-500">{timestamp}</span>
        </div>
        <p className="mt-1 text-sm text-neutral-700">{explanation}</p>
        <div className="mt-2">
          <Badge tone={severity === 'HIGH' ? 'dangerSolid' : severity === 'MEDIUM' ? 'warning' : 'info'}>
            {severity} severity
          </Badge>
        </div>
      </div>
      {acknowledged ? (
        <span className="text-xs text-neutral-500">Acknowledged</span>
      ) : (
        <Button variant="ghost" size="sm" onClick={onAcknowledge}>
          Acknowledge
        </Button>
      )}
    </div>
  )
}
