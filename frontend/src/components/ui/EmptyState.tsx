import type { ReactNode } from 'react'

export function EmptyState({
  action,
  description,
  icon,
  title,
}: {
  action?: ReactNode
  description: string
  icon?: ReactNode
  title: string
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-card border border-dashed border-neutral-300 bg-white px-6 py-12 text-center">
      {icon ? <div className="mb-4 text-neutral-300">{icon}</div> : null}
      <h3 className="text-base font-semibold text-neutral-900">{title}</h3>
      <p className="mt-2 max-w-md text-sm text-neutral-500">{description}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  )
}
