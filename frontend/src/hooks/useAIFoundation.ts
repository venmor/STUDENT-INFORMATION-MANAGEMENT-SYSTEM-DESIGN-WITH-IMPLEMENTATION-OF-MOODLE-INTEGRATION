import { useMutation, useQuery } from '@tanstack/react-query'

import {
  getAnalyticsRuns,
  getAnalyticsSnapshots,
  getAnalyticsSummary,
  getKnowledgeIngestionRuns,
  getKnowledgeSources,
  getKnowledgeSummary,
  testKnowledgeQuery,
} from '@/api/aiFoundation'
import type { KnowledgeTestQueryRequest } from '@/types/aiFoundation'

export function useAnalyticsSummary() {
  return useQuery({
    queryKey: ['ai-foundation', 'analytics-summary'],
    queryFn: getAnalyticsSummary,
  })
}

export function useAnalyticsSnapshots() {
  return useQuery({
    queryKey: ['ai-foundation', 'analytics-snapshots'],
    queryFn: getAnalyticsSnapshots,
  })
}

export function useAnalyticsRuns() {
  return useQuery({
    queryKey: ['ai-foundation', 'analytics-runs'],
    queryFn: getAnalyticsRuns,
  })
}

export function useKnowledgeSummary() {
  return useQuery({
    queryKey: ['ai-foundation', 'knowledge-summary'],
    queryFn: getKnowledgeSummary,
  })
}

export function useKnowledgeSources() {
  return useQuery({
    queryKey: ['ai-foundation', 'knowledge-sources'],
    queryFn: getKnowledgeSources,
  })
}

export function useKnowledgeIngestionRuns() {
  return useQuery({
    queryKey: ['ai-foundation', 'knowledge-ingestion-runs'],
    queryFn: getKnowledgeIngestionRuns,
  })
}

export function useKnowledgeTestQuery() {
  return useMutation({
    mutationFn: (payload: KnowledgeTestQueryRequest) => testKnowledgeQuery(payload),
  })
}
