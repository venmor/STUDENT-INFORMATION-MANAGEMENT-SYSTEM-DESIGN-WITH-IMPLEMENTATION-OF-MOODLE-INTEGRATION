import type { ReactNode } from 'react'

type BadgeTone = 'default' | 'success' | 'warning' | 'danger' | 'dangerSolid' | 'info'

export function formatNumber(value?: number | string | null) {
  return new Intl.NumberFormat().format(Number(value ?? 0))
}

export function formatPercent(value?: number | string | null) {
  if (value === null || value === undefined || value === '') {
    return 'Not available'
  }
  return `${Number(value).toFixed(2)}%`
}

export function formatDateTime(value?: string | null) {
  if (!value) {
    return 'Not available'
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export function labelFromCode(value?: string | null) {
  if (!value) {
    return 'Not available'
  }
  return value
    .toLowerCase()
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

export function toneForStatus(status?: string | null): BadgeTone {
  if (status === 'SUCCEEDED' || status === 'INGESTED' || status === 'READY') {
    return 'success'
  }
  if (status === 'FAILED') {
    return 'danger'
  }
  if (status === 'PARTIAL' || status === 'STARTED' || status === 'DRAFT') {
    return 'warning'
  }
  return 'info'
}

export function scoreText(score: number) {
  return `Score ${score.toFixed(2)}`
}

export type SummaryMetric = {
  title: string
  value: string
  helper: string
  icon: ReactNode
  tone: 'danger' | 'warning' | 'success' | 'info'
}
