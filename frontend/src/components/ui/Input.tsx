import type { InputHTMLAttributes } from 'react'

import { cn } from '@/utils/cn'

type InputProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> & {
  error?: string
  label: string
}

export function Input({ className, error, id, label, ...props }: InputProps) {
  const errorId = error && id ? `${id}-error` : undefined

  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-sm font-medium text-neutral-700">
        {label}
      </label>
      <input
        id={id}
        aria-describedby={errorId}
        className={cn(
          'block w-full rounded-lg border border-neutral-300 px-4 py-2.5 text-neutral-900 placeholder:text-neutral-400',
          'focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none',
          error && 'border-danger ring-2 ring-danger/20',
          className,
        )}
        {...props}
      />
      {error ? (
        <p id={errorId} role="alert" className="text-sm text-danger">
          {error}
        </p>
      ) : null}
    </div>
  )
}
