import { api } from '@/api/axios'
import type {
  AnalyticsETLRun,
  AnalyticsSnapshot,
  AnalyticsSummary,
  KnowledgeIngestionRun,
  KnowledgeSource,
  KnowledgeSummary,
  KnowledgeTestQueryRequest,
  KnowledgeTestQueryResponse,
} from '@/types/aiFoundation'

export async function getAnalyticsSummary() {
  const response = await api.get<AnalyticsSummary>('/admin/analytics/summary/')
  return response.data
}

export async function getAnalyticsSnapshots() {
  const response = await api.get<AnalyticsSnapshot[]>('/admin/analytics/snapshots/', { params: { limit: 10 } })
  return response.data
}

export async function getAnalyticsRuns() {
  const response = await api.get<AnalyticsETLRun[]>('/admin/analytics/etl-runs/')
  return response.data
}

export async function getKnowledgeSummary() {
  const response = await api.get<KnowledgeSummary>('/admin/knowledge/summary/')
  return response.data
}

export async function getKnowledgeSources() {
  const response = await api.get<KnowledgeSource[]>('/admin/knowledge/sources/')
  return response.data
}

export async function getKnowledgeIngestionRuns() {
  const response = await api.get<KnowledgeIngestionRun[]>('/admin/knowledge/ingestion-runs/')
  return response.data
}

export async function testKnowledgeQuery(payload: KnowledgeTestQueryRequest) {
  const response = await api.post<KnowledgeTestQueryResponse>('/admin/knowledge/test-query/', payload)
  return response.data
}
