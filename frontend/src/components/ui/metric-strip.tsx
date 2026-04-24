export function MetricStrip({
  items,
}: {
  items: Array<{ label: string; value: string; accent?: string }>
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <div
          key={item.label}
          className="rounded-[1.5rem] border border-white/70 bg-white/85 px-4 py-4 shadow-[0_16px_48px_rgba(23,33,43,0.08)]"
        >
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{item.label}</p>
          <p className={`mt-2 text-3xl font-semibold ${item.accent ?? 'text-slate-900'}`}>{item.value}</p>
        </div>
      ))}
    </div>
  )
}
