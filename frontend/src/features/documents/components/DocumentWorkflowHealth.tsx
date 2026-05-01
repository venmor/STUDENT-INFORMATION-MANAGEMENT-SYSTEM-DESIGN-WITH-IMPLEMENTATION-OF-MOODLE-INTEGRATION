import { ArchiveBoxIcon, ClockIcon, EyeIcon, ServerStackIcon } from '@heroicons/react/24/outline'

import { Card, CardTitle } from '@/components/ui/Card'
import type { DocumentSummary } from '@/types/documents'

function HealthItem({
  helper,
  icon: Icon,
  label,
  value,
}: {
  helper: string
  icon: typeof ClockIcon
  label: string
  value: string
}) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-neutral-200 bg-neutral-50 p-3">
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white text-primary shadow-sm">
        <Icon className="h-5 w-5" />
      </span>
      <div className="min-w-0">
        <p className="text-sm font-semibold text-neutral-900">{label}</p>
        <p className="mt-1 text-sm text-neutral-600">{value}</p>
        <p className="mt-1 text-xs text-neutral-500">{helper}</p>
      </div>
    </div>
  )
}

export function DocumentWorkflowHealth({
  summary,
  storageLabel = 'Local media storage',
}: {
  storageLabel?: string
  summary?: DocumentSummary
}) {
  const pendingReview = summary?.pendingReview ?? 0
  const studentVisible = summary?.studentVisible ?? 0
  const recentUploads = summary?.recentUploads ?? 0

  return (
    <Card className="p-4">
      <CardTitle>Workflow Health</CardTitle>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <HealthItem
          icon={ClockIcon}
          label="Review Queue"
          value={pendingReview > 0 ? `${pendingReview} pending review` : 'Clear'}
          helper={pendingReview > 0 ? 'Needs Review' : 'No pending document reviews'}
        />
        <HealthItem
          icon={EyeIcon}
          label="Visibility"
          value={studentVisible > 0 ? `${studentVisible} student visible` : 'Protected'}
          helper="Protected / Student Visible"
        />
        <HealthItem
          icon={ArchiveBoxIcon}
          label="Recent Activity"
          value={`${recentUploads} recent uploads`}
          helper="Uploads in the last 7 days"
        />
        <HealthItem
          icon={ServerStackIcon}
          label="Storage"
          value={storageLabel}
          helper="Protected downloads use the backend API"
        />
      </div>
    </Card>
  )
}
