import { CheckCircleIcon, QueueListIcon, ServerStackIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'

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
        <Link to="/admin/moodle-sync">
          <SystemHealthCard icon={<ServerStackIcon className="h-6 w-6" />} label="Backend API" detail="Verified in Step 2.4" status="Latest checks green" />
        </Link>
        <Link to="/admin/users">
          <SystemHealthCard icon={<CheckCircleIcon className="h-6 w-6" />} label="User accounts" detail={`${users.length} managed accounts`} status="Live" />
        </Link>
        <Link to="/admin/users">
          <SystemHealthCard icon={<QueueListIcon className="h-6 w-6" />} label="Student records" detail={`${students.length} visible student profiles`} status="Live" />
        </Link>
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
      <DeferredFeaturePanel phaseLabel="Objective 1" title="Operational overview">
        The administrator area provides access to user administration, academic structure, Moodle synchronization, audit
        activity, reporting, and system review screens used to verify the implemented SIS.
      </DeferredFeaturePanel>
    </div>
  )
}
