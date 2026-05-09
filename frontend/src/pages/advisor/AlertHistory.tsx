import { AtRiskAlertRow } from '@/components/advisor/AtRiskAlertRow'
import { useAtRiskAlertHistory } from '@/hooks/useAtRiskAlerts'

export function AdvisorAlertHistoryPage() {
  const { data: alerts, isPending, isError } = useAtRiskAlertHistory()

  if (isPending) {
    return <div className="p-4 text-sm text-neutral-500">Loading alert history...</div>
  }

  if (isError) {
    return <div className="p-4 text-sm text-red-600">Failed to load alert history.</div>
  }

  if (!alerts || alerts.length === 0) {
    return <div className="p-4 text-sm text-neutral-500">No historical alerts.</div>
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-neutral-800">Alert History</h2>
      {alerts.map((alert) => (
        <AtRiskAlertRow
          key={alert.id}
          severity={alert.severity}
          studentName={`${alert.student_name} (${alert.student_number})`}
          timestamp={new Date(alert.updated_at).toLocaleDateString()}
          explanation={alert.explanation || `Signals: ${alert.active_signals.join(', ')}`}
          acknowledged
        />
      ))}
    </div>
  )
}
