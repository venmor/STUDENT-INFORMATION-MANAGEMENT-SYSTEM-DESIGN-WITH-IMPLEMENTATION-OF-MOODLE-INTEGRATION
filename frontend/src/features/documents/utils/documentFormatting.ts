export function formatFileSize(bytes?: number | null) {
  const value = bytes ?? 0
  if (value < 1024) {
    return `${value} B`
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`
  }
  return `${(value / (1024 * 1024)).toFixed(1)} MB`
}

export function formatDocumentDate(value?: string | null) {
  if (!value) {
    return 'Not recorded'
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export function filenameFromContentDisposition(contentDisposition?: string) {
  if (!contentDisposition) {
    return ''
  }
  const utfMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i)
  if (utfMatch?.[1]) {
    return decodeURIComponent(utfMatch[1].replace(/"/g, ''))
  }
  const match = contentDisposition.match(/filename="?([^";]+)"?/i)
  return match?.[1] ?? ''
}
