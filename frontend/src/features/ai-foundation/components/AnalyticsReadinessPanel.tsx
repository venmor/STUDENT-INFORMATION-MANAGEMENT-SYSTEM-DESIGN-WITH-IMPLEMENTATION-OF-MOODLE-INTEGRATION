import { Link } from 'react-router-dom'

import { Badge } from '@/components/ui/Badge'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHead,
  DataTableHeader,
  DataTableRow,
  TableSkeleton,
} from '@/components/ui/Table'
import type { AnalyticsETLRun, AnalyticsSnapshot, AnalyticsSummary } from '@/types/aiFoundation'
import { formatDateTime, formatNumber, formatPercent, labelFromCode, toneForStatus } from '@/features/ai-foundation/utils/formatting'

export function AnalyticsReadinessPanel({
  isLoading,
  runs,
  snapshots,
  summary,
}: {
  isLoading: boolean
  runs: AnalyticsETLRun[]
  snapshots: AnalyticsSnapshot[]
  summary?: AnalyticsSummary
}) {
  const latestRun = summary?.latestRun ?? runs[0]

  return (
    <Card>
      <div className="flex flex-col gap-3 border-b border-neutral-100 pb-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <CardTitle className="text-lg">Analytics Readiness</CardTitle>
          <p className="mt-1 text-sm text-neutral-600">
            Derived SIS and stored Moodle engagement signals for future governed analytics features.
          </p>
        </div>
        <Link
          to="/admin/reports"
          className="inline-flex min-h-11 items-center rounded-lg border border-primary px-4 text-sm font-semibold text-primary transition-colors hover:bg-primary-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
        >
          Open Reports
        </Link>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <Metric label="Latest status" value={labelFromCode(latestRun?.status ?? 'Not run')} badgeStatus={latestRun?.status} />
        <Metric label="Snapshots created" value={formatNumber(latestRun?.snapshotsCreated)} />
        <Metric label="Snapshots updated" value={formatNumber(latestRun?.snapshotsUpdated)} />
        <Metric label="Failures" value={formatNumber(latestRun?.failureCount)} badgeStatus={latestRun?.failureCount ? 'FAILED' : 'SUCCEEDED'} />
      </div>

      <div className="mt-6">
        {isLoading ? (
          <TableSkeleton columns={7} />
        ) : snapshots.length === 0 ? (
          <EmptyState title="No analytics snapshots found" description="Run seed_analytics_demo and run_analytics_etl to populate this readiness view." />
        ) : (
          <DataTable ariaLabel="Student analytics snapshots">
            <DataTableHead>
              <DataTableRow>
                <DataTableHeader>Student</DataTableHeader>
                <DataTableHeader>Term</DataTableHeader>
                <DataTableHeader>Attendance</DataTableHeader>
                <DataTableHeader>Enrollments</DataTableHeader>
                <DataTableHeader>Official Grades</DataTableHeader>
                <DataTableHeader>Financial Flags</DataTableHeader>
                <DataTableHeader>Updated</DataTableHeader>
              </DataTableRow>
            </DataTableHead>
            <DataTableBody>
              {snapshots.map((snapshot) => (
                <DataTableRow key={snapshot.id}>
                  <DataTableCell>
                    <div className="font-medium">{snapshot.student.fullName}</div>
                    <div className="mt-1 text-xs text-neutral-500">{snapshot.student.studentNumber}</div>
                  </DataTableCell>
                  <DataTableCell>
                    <div>{snapshot.academicYear}</div>
                    <div className="mt-1 text-xs text-neutral-500">{snapshot.semester}</div>
                  </DataTableCell>
                  <DataTableCell>{formatPercent(snapshot.attendanceAverage)}</DataTableCell>
                  <DataTableCell>{formatNumber(snapshot.activeEnrollmentCount)}</DataTableCell>
                  <DataTableCell>{formatNumber(snapshot.officialGradeCount)}</DataTableCell>
                  <DataTableCell>{formatNumber(snapshot.financialFlagCount)}</DataTableCell>
                  <DataTableCell>{formatDateTime(snapshot.updatedAt)}</DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        )}
      </div>
    </Card>
  )
}

function Metric({ badgeStatus, label, value }: { badgeStatus?: string | null; label: string; value: string }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-neutral-50 px-3 py-2">
      <p className="text-xs font-medium uppercase tracking-[0.12em] text-neutral-500">{label}</p>
      {badgeStatus ? (
        <Badge tone={toneForStatus(badgeStatus)} className="mt-2">
          {value}
        </Badge>
      ) : (
        <p className="mt-2 text-sm font-semibold text-neutral-900">{value}</p>
      )}
    </div>
  )
}
