import type { CopilotSource } from '@/types/copilot'

function sourceRoute(sourceType: string) {
  if (sourceType === 'ACADEMIC_CALENDAR') return '/calendar'
  if (sourceType === 'REGISTRATION_PROCEDURES') return '/student/register'
  if (sourceType === 'COURSE_CATALOG') return '/student/courses'
  return ''
}

export function CopilotSourcePanel({ sources }: { sources: CopilotSource[] }) {
  return (
    <aside aria-label="Co-pilot source references" className="rounded-lg border border-neutral-200 bg-white p-4">
      <div>
        <h2 className="text-base font-semibold text-neutral-900">Sources</h2>
        <p className="mt-1 text-sm text-neutral-500">Institutional chunks used for the latest answer.</p>
      </div>
      <div className="mt-4 space-y-3">
        {sources.length === 0 ? (
          <p className="rounded-lg border border-dashed border-neutral-300 bg-neutral-50 p-4 text-sm text-neutral-600">
            Source references will appear here after a grounded answer.
          </p>
        ) : null}
        {sources.map((source) => {
          const route = sourceRoute(source.sourceType)
          return (
            <article key={source.chunkId} className="rounded-lg border border-neutral-200 bg-neutral-50 p-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-sm font-semibold text-neutral-900">{source.title}</h3>
                  <p className="mt-1 text-xs font-medium uppercase tracking-wide text-neutral-500">{source.sourceType}</p>
                </div>
                <span className="shrink-0 rounded-full border border-primary/20 bg-primary-light px-2 py-1 text-xs font-semibold text-primary">
                  Relevance {source.score}
                </span>
              </div>
              <p className="mt-3 text-sm leading-6 text-neutral-700">{source.preview}</p>
              {route ? (
                <a
                  href={route}
                  className="mt-3 inline-flex min-h-11 items-center text-sm font-semibold text-primary hover:text-primary-dark focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                >
                  Open related page
                </a>
              ) : null}
            </article>
          )
        })}
      </div>
    </aside>
  )
}
