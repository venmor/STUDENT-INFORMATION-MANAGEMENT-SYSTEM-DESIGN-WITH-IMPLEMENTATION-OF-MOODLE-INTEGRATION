import { Link } from 'react-router-dom'

import type { CopilotSuggestedAction } from '@/types/copilot'

export function CopilotSuggestedActions({ actions }: { actions: CopilotSuggestedAction[] }) {
  if (!actions.length) {
    return null
  }

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      {actions.map((action) => (
        <Link
          key={`${action.label}-${action.url}`}
          to={action.url}
          className="inline-flex min-h-11 items-center rounded-lg border border-primary/20 bg-white px-3 text-sm font-semibold text-primary transition-colors hover:bg-primary-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
        >
          {action.label}
        </Link>
      ))}
    </div>
  )
}
