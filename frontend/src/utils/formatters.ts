export function formatDate(value?: string | null) {
  if (!value) {
    return '—'
  }

  return new Intl.DateTimeFormat('en-ZM', {
    dateStyle: 'medium',
  }).format(new Date(value))
}

export function formatDateTime(value?: string | null) {
  if (!value) {
    return '—'
  }

  return new Intl.DateTimeFormat('en-ZM', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export function formatGpa(value?: string | null) {
  if (!value) {
    return '0.00'
  }

  return Number(value).toFixed(2)
}

export function formatPercentage(value?: string | null) {
  if (!value) {
    return '0%'
  }

  return `${Math.round(Number(value))}%`
}
