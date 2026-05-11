import { Alert } from '@/components/ui/Alert'
import { AIFoundationScopeNote } from '@/features/ai-foundation/components/AIFoundationScopeNote'
import { AIFoundationSummaryCards } from '@/features/ai-foundation/components/AIFoundationSummaryCards'
import { AnalyticsReadinessPanel } from '@/features/ai-foundation/components/AnalyticsReadinessPanel'
import { KnowledgeBasePanel } from '@/features/ai-foundation/components/KnowledgeBasePanel'
import { RetrievalTestPanel } from '@/features/ai-foundation/components/RetrievalTestPanel'
import {
  useAnalyticsRuns,
  useAnalyticsSnapshots,
  useAnalyticsSummary,
  useKnowledgeIngestionRuns,
  useKnowledgeSources,
  useKnowledgeSummary,
  useKnowledgeTestQuery,
} from '@/hooks/useAIFoundation'

export function AdminAIFoundationPage() {
  const analyticsSummary = useAnalyticsSummary()
  const analyticsSnapshots = useAnalyticsSnapshots()
  const analyticsRuns = useAnalyticsRuns()
  const knowledgeSummary = useKnowledgeSummary()
  const knowledgeSources = useKnowledgeSources()
  const knowledgeRuns = useKnowledgeIngestionRuns()
  const retrieval = useKnowledgeTestQuery()

  const analyticsLoading = analyticsSummary.isLoading || analyticsSnapshots.isLoading || analyticsRuns.isLoading
  const knowledgeLoading = knowledgeSummary.isLoading || knowledgeSources.isLoading || knowledgeRuns.isLoading

  return (
    <div className="space-y-6">
      {analyticsSummary.isError || analyticsSnapshots.isError || analyticsRuns.isError ? (
        <Alert tone="danger">Could not load analytics foundation status</Alert>
      ) : null}
      {knowledgeSummary.isError || knowledgeSources.isError || knowledgeRuns.isError ? (
        <Alert tone="danger">Could not load knowledge foundation status</Alert>
      ) : null}

      <AIFoundationSummaryCards analytics={analyticsSummary.data} knowledge={knowledgeSummary.data} isLoading={analyticsSummary.isLoading} />

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <AnalyticsReadinessPanel
          summary={analyticsSummary.data}
          snapshots={analyticsSnapshots.data ?? []}
          runs={analyticsRuns.data ?? []}
          isLoading={analyticsLoading}
        />
        <KnowledgeBasePanel
          summary={knowledgeSummary.data}
          sources={knowledgeSources.data ?? []}
          runs={knowledgeRuns.data ?? []}
          isLoading={knowledgeLoading}
        />
      </div>

      <RetrievalTestPanel
        data={retrieval.data}
        isPending={retrieval.isPending}
        onRun={(query) => retrieval.mutate({ query, limit: 5 })}
      />

      <AIFoundationScopeNote />
    </div>
  )
}
