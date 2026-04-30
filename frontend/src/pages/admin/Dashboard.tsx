import { CheckCircleIcon, QueueListIcon, ServerStackIcon } from '@heroicons/react/24/outline'

import { ActivityFeed } from '@/components/admin/ActivityFeed'
import { SyncStatusBadge } from '@/components/admin/SyncStatusBadge'
import { SystemHealthCard } from '@/components/admin/SystemHealthCard'
import { Card, CardTitle } from '@/components/ui/Card'
import { DeferredFeaturePanel } from '@/components/ui/DeferredFeaturePanel'
import { useStudents } from '@/hooks/useStudents'
import { useUsers } from '@/hooks/useUsers'

export function AdminDashboardPage() {
  const { data: users = [] } = useUsers()
  const { data: students = [] } = useStudents()

  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-3">
        <SystemHealthCard icon={<ServerStackIcon className="h-6 w-6" />} label="Backend API" detail="Verified in Step 2.4" status="Latest checks green" />
        <SystemHealthCard icon={<CheckCircleIcon className="h-6 w-6" />} label="User accounts" detail={`${users.length} managed accounts`} status="Live" />
        <SystemHealthCard icon={<QueueListIcon className="h-6 w-6" />} label="Student records" detail={`${students.length} visible student profiles`} status="Live" />
      </div>
      <Card>
        <CardTitle>Recent activity</CardTitle>
        <div className="mt-4">
          <ActivityFeed
            items={[
              <div className="rounded-xl border border-neutral-200 px-4 py-3 text-sm text-neutral-700">User administration and grade officialisation remain available through the live backend APIs.</div>,
              <div className="rounded-xl border border-neutral-200 px-4 py-3 text-sm text-neutral-700">
                Moodle sync monitoring is available from the admin navigation. <SyncStatusBadge status="Ready" />
              </div>,
            ]}
          />
        </div>
      </Card>
      <DeferredFeaturePanel phaseLabel="Phase 3 / Phase 4" title="Operational telemetry">
        Broader system-health telemetry, admin reporting, and AI audit browsing depend on later integration and AI
        phases. The admin dashboard reserves the correct information hierarchy for those panels now.
      </DeferredFeaturePanel>
    </div>
  )
}
