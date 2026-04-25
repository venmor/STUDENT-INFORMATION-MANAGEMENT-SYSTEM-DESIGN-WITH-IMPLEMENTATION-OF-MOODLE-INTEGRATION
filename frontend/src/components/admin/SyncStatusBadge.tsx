import { Badge } from '@/components/ui/Badge'

export function SyncStatusBadge({ status }: { status: 'Deferred' | 'Ready' }) {
  return <Badge tone={status === 'Ready' ? 'success' : 'warning'}>{status}</Badge>
}
