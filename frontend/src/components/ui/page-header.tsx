import type { ReactNode } from 'react'

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow: string
  title: string
  description: string
  actions?: ReactNode
}) {
  return (
    <header className="rounded-[2rem] border border-slate-900/10 bg-slate-900 px-6 py-8 text-white shadow-[0_24px_80px_rgba(15,23,42,0.24)]">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-3xl">
          <p className="text-xs uppercase tracking-[0.32em] text-orange-200">{eyebrow}</p>
          <h1 className="mt-3 text-3xl font-semibold sm:text-4xl">{title}</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-200 sm:text-base">{description}</p>
        </div>
        {actions}
      </div>
    </header>
  )
}
