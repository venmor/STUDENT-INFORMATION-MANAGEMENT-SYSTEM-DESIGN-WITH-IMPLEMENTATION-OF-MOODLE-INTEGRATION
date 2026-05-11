import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'

export function StudentSearchBar({
  onChange,
  value,
}: {
  onChange: (value: string) => void
  value: string
}) {
  return (
    <div className="relative">
      <MagnifyingGlassIcon className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-neutral-400" />
      <input
        className="w-full rounded-xl border border-neutral-300 bg-white py-3 pl-11 pr-4 text-sm text-neutral-900 placeholder:text-neutral-400 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
        placeholder="Search by student name or student number"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  )
}
