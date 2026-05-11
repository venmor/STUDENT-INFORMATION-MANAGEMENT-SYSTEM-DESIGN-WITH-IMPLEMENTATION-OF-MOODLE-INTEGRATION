import type { TextareaHTMLAttributes } from 'react'

import { cn } from '@/utils/cn'

type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  error?: string
  hint?: string
  label: string
}

export function Textarea({ className, error, hint, id, label, rows = 4, ...props }: TextareaProps) {
  const describedBy = [hint && id ? `${id}-hint` : null, error && id ? `${id}-error` : null]
    .filter(Boolean)
    .join(' ')

  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-sm font-medium text-neutral-700">
        {label}
      </label>
      <textarea
        id={id}
        rows={rows}
        aria-describedby={describedBy || undefined}
        className={cn(
          'block w-full rounded-lg border border-neutral-300 px-4 py-2.5 text-neutral-900 placeholder:text-neutral-400',
          'focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none',
          error && 'border-danger ring-2 ring-danger/20',
          className,
        )}
        {...props}
      />
      {hint ? (
        <p id={id ? `${id}-hint` : undefined} className="text-sm text-neutral-500">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={id ? `${id}-error` : undefined} role="alert" className="text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  )
}
