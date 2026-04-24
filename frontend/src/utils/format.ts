export function formatDate(value: string | null | undefined) {
  if (!value) {
    return 'Not set'
  }

  return new Intl.DateTimeFormat('en-ZM', {
    dateStyle: 'medium',
  }).format(new Date(value))
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return 'Not set'
  }

  return new Intl.DateTimeFormat('en-ZM', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export function formatDecimal(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === '') {
    return '0.00'
  }

  return Number(value).toFixed(2)
}

export function isOpenWindow(openAt: string, closeAt: string) {
  const now = Date.now()
  return now >= new Date(openAt).getTime() && now <= new Date(closeAt).getTime()
}
