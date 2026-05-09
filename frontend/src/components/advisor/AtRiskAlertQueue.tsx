import { AtRiskAlertRow } from '@/components/advisor/AtRiskAlertRow'
import { useAcknowledgeAlertMutation, useAtRiskAlerts } from '@/hooks/useAtRiskAlerts'

export function AtRiskAlertQueue() {
  const { data: alerts, isPending, isError } = useAtRiskAlerts()
  const acknowledgeMutation = useAcknowledgeAlertMutation()

  if (isPending) {
    return <div className="p-4 text-sm text-neutral-500">Loading at-risk alerts...</div>
  }

  if (isError) {
    return <div className="p-4 text-sm text-red-600">Failed to load at-risk alerts.</div>
  }

  if (!alerts || alerts.length === 0) {
    return <div className="p-4 text-sm text-neutral-500">No open at-risk alerts.</div>
  }

  return (
    <div className="space-y-4">
      {alerts.map((alert) => (
        <AtRiskAlertRow
          key={alert.id}
          severity={alert.severity}
          studentName={`${alert.student_name} (${alert.student_number})`}
          timestamp={new Date(alert.created_at).toLocaleDateString()}
          explanation={alert.explanation || `Signals: ${alert.active_signals.join(', ')}`}
          onAcknowledge={() => acknowledgeMutation.mutate(alert.id)}
        />
      ))}
    </div>
  )
}
