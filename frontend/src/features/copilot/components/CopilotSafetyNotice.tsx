import { ShieldCheckIcon } from '@heroicons/react/24/outline'

export function CopilotSafetyNotice() {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-900">
      <ShieldCheckIcon className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
      <div>
        <p>Responses are generated from institutional sources and your safe student context.</p>
        <p className="mt-1">They do not create official records or change your enrolments, grades, or documents.</p>
      </div>
    </div>
  )
}
