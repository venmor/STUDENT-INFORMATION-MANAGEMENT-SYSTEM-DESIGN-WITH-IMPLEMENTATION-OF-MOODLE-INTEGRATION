import { AtRiskAlertRow } from '@/components/advisor/AtRiskAlertRow'
import { useAtRiskAlertHistory } from '@/hooks/useAtRiskAlerts'

export function AdvisorAlertHistoryPage() {
  const { data: alerts, isPending, isError } = useAtRiskAlertHistory()

  if (isPending) {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-neutral-200 bg-neutral-50 p-4">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-neutral-300 border-t-blue-600" />
        <div>
          <p className="text-sm font-medium text-neutral-700">Loading alert history...</p>
          <p className="text-xs text-neutral-500">Fetching acknowledged alerts from the server.</p>
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4">
        <p className="text-sm font-medium text-red-700">Failed to load alert history</p>
        <p className="mt-1 text-xs text-red-600">The request failed after multiple retries. Please check your connection and try again.</p>
      </div>
    )
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
