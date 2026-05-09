import { AtRiskAlertRow } from '@/components/advisor/AtRiskAlertRow'
import { useAcknowledgeAlertMutation, useAtRiskAlerts } from '@/hooks/useAtRiskAlerts'

export function AtRiskAlertQueue() {
  const { data: alerts, isPending, isError, isFetching } = useAtRiskAlerts()
  const acknowledgeMutation = useAcknowledgeAlertMutation()

  if (isPending) {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-neutral-200 bg-neutral-50 p-4">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-neutral-300 border-t-blue-600" />
        <div>
          <p className="text-sm font-medium text-neutral-700">AI is processing alerts...</p>
          <p className="text-xs text-neutral-500">The at-risk engine is evaluating student signals. This may take a moment.</p>
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4">
        <p className="text-sm font-medium text-red-700">Failed to load at-risk alerts</p>
        <p className="mt-1 text-xs text-red-600">The request failed after multiple retries. Please check your connection and try again.</p>
      </div>
    )
  }

  if (!alerts || alerts.length === 0) {
    return <div className="p-4 text-sm text-neutral-500">No open at-risk alerts.</div>
  }

  return (
    <div className="space-y-4">
      {isFetching && (
        <div className="flex items-center gap-2 rounded-md bg-blue-50 px-3 py-2 text-xs text-blue-700">
          <div className="h-3 w-3 animate-spin rounded-full border border-blue-300 border-t-blue-600" />
          Refreshing alerts...
        </div>
      )}
      {acknowledgeMutation.isPending && (
        <div className="flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700">
          <div className="h-3 w-3 animate-spin rounded-full border border-amber-300 border-t-amber-600" />
          Processing acknowledgement... Please wait.
        </div>
      )}
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
