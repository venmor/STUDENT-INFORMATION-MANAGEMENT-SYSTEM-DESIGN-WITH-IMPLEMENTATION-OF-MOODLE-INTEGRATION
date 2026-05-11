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
import type { KnowledgeIngestionRun, KnowledgeSource, KnowledgeSummary } from '@/types/aiFoundation'
import { formatDateTime, formatNumber, labelFromCode, toneForStatus } from '@/features/ai-foundation/utils/formatting'

export function KnowledgeBasePanel({
  isLoading,
  runs,
  sources,
  summary,
}: {
  isLoading: boolean
  runs: KnowledgeIngestionRun[]
  sources: KnowledgeSource[]
  summary?: KnowledgeSummary
}) {
  const latestRun = summary?.latestIngestion ?? runs[0]

  return (
    <Card>
      <div className="border-b border-neutral-100 pb-4">
        <CardTitle className="text-lg">Knowledge Base</CardTitle>
        <p className="mt-1 text-sm text-neutral-600">
          Institutional source metadata and chunk readiness for retrieval-only testing.
        </p>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <Metric label="Sources" value={formatNumber(summary?.sources ?? sources.length)} />
        <Metric label="Chunks" value={formatNumber(summary?.chunks ?? sources.reduce((sum, source) => sum + source.chunkCount, 0))} />
        <Metric label="Latest ingestion" value={labelFromCode(latestRun?.status ?? 'Not run')} badgeStatus={latestRun?.status} />
        <Metric label="Vector health" value={summary?.vectorStore?.healthy ? 'Ready' : 'Needs attention'} badgeStatus={summary?.vectorStore?.healthy ? 'SUCCEEDED' : 'PARTIAL'} />
      </div>

      <div className="mt-6">
        {isLoading ? (
          <TableSkeleton columns={6} />
        ) : sources.length === 0 ? (
          <EmptyState title="No knowledge sources found" description="Run seed_knowledge_demo and ingest_knowledge_base to prepare demo institutional sources." />
        ) : (
          <DataTable ariaLabel="Institutional knowledge sources">
            <DataTableHead>
              <DataTableRow>
                <DataTableHeader>Source</DataTableHeader>
                <DataTableHeader>Type</DataTableHeader>
                <DataTableHeader>Visibility</DataTableHeader>
                <DataTableHeader>Status</DataTableHeader>
                <DataTableHeader>Chunks</DataTableHeader>
                <DataTableHeader>Updated</DataTableHeader>
              </DataTableRow>
            </DataTableHead>
            <DataTableBody>
              {sources.map((source) => (
                <DataTableRow key={source.id}>
                  <DataTableCell>
                    <div className="font-medium">{source.title}</div>
                    {source.description ? <div className="mt-1 max-w-xl truncate text-xs text-neutral-500">{source.description}</div> : null}
                  </DataTableCell>
                  <DataTableCell>{labelFromCode(source.sourceType)}</DataTableCell>
                  <DataTableCell>
                    <Badge tone="info">{labelFromCode(source.visibility)}</Badge>
                  </DataTableCell>
                  <DataTableCell>
                    <Badge tone={toneForStatus(source.status)}>{labelFromCode(source.status)}</Badge>
                  </DataTableCell>
                  <DataTableCell>{formatNumber(source.chunkCount)}</DataTableCell>
                  <DataTableCell>{formatDateTime(source.updatedAt)}</DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        )}
      </div>

      {runs.length > 0 ? (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-neutral-900">Recent Ingestion Runs</h3>
          <DataTable ariaLabel="Knowledge ingestion runs" className="mt-3">
            <DataTableHead>
              <DataTableRow>
                <DataTableHeader>Status</DataTableHeader>
                <DataTableHeader>Sources</DataTableHeader>
                <DataTableHeader>Chunks</DataTableHeader>
                <DataTableHeader>Upserted</DataTableHeader>
                <DataTableHeader>Failures</DataTableHeader>
                <DataTableHeader>Completed</DataTableHeader>
              </DataTableRow>
            </DataTableHead>
            <DataTableBody>
              {runs.slice(0, 5).map((run) => (
                <DataTableRow key={run.id}>
                  <DataTableCell>
                    <Badge tone={toneForStatus(run.status)}>{labelFromCode(run.status)}</Badge>
                  </DataTableCell>
                  <DataTableCell>{formatNumber(run.sourcesProcessed)}</DataTableCell>
                  <DataTableCell>{formatNumber(run.chunksCreated)}</DataTableCell>
                  <DataTableCell>{formatNumber(run.chunksUpserted)}</DataTableCell>
                  <DataTableCell>{formatNumber(run.failureCount)}</DataTableCell>
                  <DataTableCell>{formatDateTime(run.completedAt)}</DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        </div>
      ) : null}
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
