export function ForbiddenPage() {
  return (
    <div className="rounded-[2rem] border border-red-200 bg-red-50 px-6 py-8 text-slate-900">
      <p className="text-xs uppercase tracking-[0.32em] text-red-500">403</p>
      <h1 className="mt-3 text-3xl font-semibold">Forbidden</h1>
      <p className="mt-3 max-w-2xl text-sm text-slate-700">
        This route is protected by the role model defined in the SRS and the backend access-policy registry.
      </p>
    </div>
  )
}

export default ForbiddenPage
