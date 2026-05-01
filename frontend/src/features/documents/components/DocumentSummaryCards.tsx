import type { ReactNode } from 'react'
import {
  ArchiveBoxIcon,
  CheckCircleIcon,
  ClockIcon,
  DocumentTextIcon,
  EyeIcon,
  XCircleIcon,
  ArrowUpTrayIcon,
} from '@heroicons/react/24/outline'

import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import type { DocumentSummary } from '@/types/documents'

type Accent = 'danger' | 'warning' | 'success' | 'info'

function numberValue(value?: number) {
  return new Intl.NumberFormat().format(value ?? 0)
}

function SummaryCard({
  accent,
  helper,
  icon,
  loading,
  title,
  value,
}: {
  accent: Accent
  helper: string
  icon: ReactNode
  loading?: boolean
  title: string
  value: number
}) {
  return (
    <Card accent={accent} className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-medium text-neutral-500">{title}</p>
          {loading ? (
            <Skeleton className="mt-2 h-8 w-20" />
          ) : (
            <p className="mt-2 font-display text-2xl font-semibold text-neutral-900">{numberValue(value)}</p>
          )}
          <p className="mt-1 text-xs text-neutral-500">{helper}</p>
        </div>
        <div className="rounded-lg bg-white p-2 text-primary shadow-sm">{icon}</div>
      </div>
    </Card>
  )
}

export function DocumentSummaryCards({
  context = 'admin',
  isLoading = false,
  summary,
}: {
  context?: 'admin' | 'student'
  isLoading?: boolean
  summary?: DocumentSummary
}) {
  const cards =
    context === 'student'
      ? [
          {
            title: 'Shared Documents',
            value: summary?.total ?? 0,
            helper: 'Student-visible records',
            accent: 'info' as Accent,
            icon: <DocumentTextIcon className="h-5 w-5" />,
          },
          {
            title: 'Pending Review',
            value: summary?.pendingReview ?? 0,
            helper: 'Awaiting institutional review',
            accent: 'warning' as Accent,
            icon: <ClockIcon className="h-5 w-5" />,
          },
          {
            title: 'Approved',
            value: summary?.approved ?? 0,
            helper: 'Reviewed and accepted',
            accent: 'success' as Accent,
            icon: <CheckCircleIcon className="h-5 w-5" />,
          },
          {
            title: 'Rejected',
            value: summary?.rejected ?? 0,
            helper: 'Needs attention',
            accent: 'danger' as Accent,
            icon: <XCircleIcon className="h-5 w-5" />,
          },
        ]
      : [
          {
            title: 'Total Documents',
            value: summary?.total ?? 0,
            helper: 'All protected records',
            accent: 'info' as Accent,
            icon: <DocumentTextIcon className="h-5 w-5" />,
          },
          {
            title: 'Pending Review',
            value: summary?.pendingReview ?? 0,
            helper: 'Needs admin action',
            accent: 'warning' as Accent,
            icon: <ClockIcon className="h-5 w-5" />,
          },
          {
            title: 'Approved',
            value: summary?.approved ?? 0,
            helper: 'Reviewed records',
            accent: 'success' as Accent,
            icon: <CheckCircleIcon className="h-5 w-5" />,
          },
          {
            title: 'Rejected',
            value: summary?.rejected ?? 0,
            helper: 'Returned documents',
            accent: 'danger' as Accent,
            icon: <XCircleIcon className="h-5 w-5" />,
          },
          {
            title: 'Archived',
            value: summary?.archived ?? 0,
            helper: 'Retained but inactive',
            accent: 'info' as Accent,
            icon: <ArchiveBoxIcon className="h-5 w-5" />,
          },
          {
            title: 'Student Visible',
            value: summary?.studentVisible ?? 0,
            helper: 'Visible to students',
            accent: 'success' as Accent,
            icon: <EyeIcon className="h-5 w-5" />,
          },
          {
            title: 'Recent Uploads',
            value: summary?.recentUploads ?? 0,
            helper: 'Last 7 days',
            accent: 'info' as Accent,
            icon: <ArrowUpTrayIcon className="h-5 w-5" />,
          },
        ]

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <SummaryCard key={card.title} {...card} loading={isLoading} />
      ))}
    </div>
  )
}
