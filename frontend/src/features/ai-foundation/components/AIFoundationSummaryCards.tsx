import {
  CircleStackIcon,
  ClockIcon,
  CpuChipIcon,
  DocumentTextIcon,
  RectangleStackIcon,
  ServerStackIcon,
} from '@heroicons/react/24/outline'

import { Alert } from '@/components/ui/Alert'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import type { AnalyticsSummary, KnowledgeSummary } from '@/types/aiFoundation'
import { formatNumber, formatDateTime, labelFromCode, type SummaryMetric } from '@/features/ai-foundation/utils/formatting'

function SummaryCard({ metric }: { metric: SummaryMetric }) {
  return (
    <Card accent={metric.tone} className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-medium text-neutral-500">{metric.title}</p>
          <p className="mt-2 truncate font-display text-2xl font-semibold text-neutral-900">{metric.value}</p>
          <p className="mt-1 text-xs text-neutral-500">{metric.helper}</p>
        </div>
        <div className="rounded-lg bg-white p-2 text-primary shadow-sm">{metric.icon}</div>
      </div>
    </Card>
  )
}

export function AIFoundationSummaryCards({
  analytics,
  isLoading,
  knowledge,
}: {
  analytics?: AnalyticsSummary
  isLoading: boolean
  knowledge?: KnowledgeSummary
}) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        <Alert tone="info">Loading AI foundation summary</Alert>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <Card key={index} className="p-4">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="mt-4 h-8 w-24" />
              <Skeleton className="mt-3 h-3 w-40" />
            </Card>
          ))}
        </div>
      </div>
    )
  }

  const metrics: SummaryMetric[] = [
    {
      title: 'Latest ETL Run',
      value: labelFromCode(analytics?.latestRun?.status ?? 'Not run'),
      helper: analytics?.latestRun ? `Completed ${formatDateTime(analytics.latestRun.completedAt)}` : 'Run analytics ETL to populate snapshots.',
      icon: <ClockIcon className="h-5 w-5" />,
      tone: analytics?.latestRun?.status === 'FAILED' ? 'danger' : analytics?.latestRun?.status === 'PARTIAL' ? 'warning' : 'success',
    },
    {
      title: 'Student Snapshots',
      value: formatNumber(analytics?.studentsWithSnapshots),
      helper: `${formatNumber(analytics?.moodleSnapshotsUsed)} stored Moodle snapshots used`,
      icon: <RectangleStackIcon className="h-5 w-5" />,
      tone: 'info',
    },
    {
      title: 'Knowledge Sources',
      value: formatNumber(knowledge?.sources),
      helper: 'Institutional, non-student-private sources',
      icon: <DocumentTextIcon className="h-5 w-5" />,
      tone: 'info',
    },
    {
      title: 'Knowledge Chunks',
      value: formatNumber(knowledge?.chunks),
      helper: 'Chunk records prepared for retrieval',
      icon: <CircleStackIcon className="h-5 w-5" />,
      tone: 'success',
    },
    {
      title: 'Vector Store',
      value: knowledge?.vectorStore?.healthy ? 'Ready' : 'Needs attention',
      helper: `${knowledge?.vectorStore?.provider ?? 'qdrant'} / ${knowledge?.vectorStore?.collection ?? 'modern_sis_knowledge'}`,
      icon: <ServerStackIcon className="h-5 w-5" />,
      tone: knowledge?.vectorStore?.healthy ? 'success' : 'warning',
    },
    {
      title: 'Latest Ingestion',
      value: labelFromCode(knowledge?.latestIngestion?.status ?? 'Not run'),
      helper: knowledge?.latestIngestion ? `${formatNumber(knowledge.latestIngestion.chunksUpserted)} chunks upserted` : 'Run knowledge ingestion after seeding sources.',
      icon: <CpuChipIcon className="h-5 w-5" />,
      tone: knowledge?.latestIngestion?.status === 'FAILED' ? 'danger' : knowledge?.latestIngestion?.status === 'PARTIAL' ? 'warning' : 'success',
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {metrics.map((metric) => (
        <SummaryCard key={metric.title} metric={metric} />
      ))}
    </div>
  )
}
