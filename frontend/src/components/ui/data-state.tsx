export function DataState({
  title,
  message,
}: {
  title: string
  message: string
}) {
  return (
    <div className="rounded-[1.5rem] border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-600">
      <p className="font-semibold text-slate-900">{title}</p>
      <p className="mt-1">{message}</p>
    </div>
  )
}
