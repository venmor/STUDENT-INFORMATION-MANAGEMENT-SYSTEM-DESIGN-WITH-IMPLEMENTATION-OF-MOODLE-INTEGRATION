import { useState, type FormEvent } from 'react'
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'

import { Alert } from '@/components/ui/Alert'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { Input } from '@/components/ui/Input'
import type { KnowledgeTestQueryResponse } from '@/types/aiFoundation'
import { labelFromCode, scoreText } from '@/features/ai-foundation/utils/formatting'

export function RetrievalTestPanel({
  data,
  isPending,
  onRun,
}: {
  data?: KnowledgeTestQueryResponse
  isPending: boolean
  onRun: (query: string) => void
}) {
  const [query, setQuery] = useState('What is the deadline to drop a course?')
  const [error, setError] = useState('')

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmed = query.trim()
    if (!trimmed) {
      setError('Enter a retrieval query before running the test.')
      return
    }
    setError('')
    onRun(trimmed)
  }

  const results = data?.results ?? []

  return (
    <Card>
      <div className="border-b border-neutral-100 pb-4">
        <CardTitle className="text-lg">Retrieval Test</CardTitle>
        <p className="mt-1 text-sm text-neutral-600">
          Search institutional chunks with the configured embedding provider and vector store. No generated answer is produced.
        </p>
      </div>

      <form className="mt-4 grid gap-3 md:grid-cols-[1fr_auto]" onSubmit={handleSubmit}>
        <Input
          id="knowledge-test-query"
          label="Test retrieval query"
          placeholder="What is the deadline to drop a course?"
          value={query}
          error={error}
          onChange={(event) => setQuery(event.target.value)}
        />
        <Button type="submit" loading={isPending} className="mt-0 self-end" icon={<MagnifyingGlassIcon className="h-5 w-5" />}>
          Run Retrieval Test
        </Button>
      </form>

      {data?.generatedAnswer === null ? (
        <Alert tone="info" className="mt-4">
          Retrieval only. The API returned source chunks and did not generate an answer.
        </Alert>
      ) : null}

      <div className="mt-5 space-y-3">
        {results.length === 0 ? (
          <EmptyState title="No retrieval results yet" description="Run the default query after seeding and ingesting the demo knowledge base." />
        ) : (
          results.map((result) => (
            <article key={result.chunkId} className="rounded-lg border border-neutral-200 bg-neutral-50 p-4">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <h3 className="font-semibold text-neutral-900">{result.sourceTitle || 'Untitled source'}</h3>
                  <p className="mt-1 text-xs text-neutral-500">
                    {labelFromCode(result.sourceType)} / Chunk ID {result.chunkId}
                  </p>
                </div>
                <Badge tone="success">{scoreText(result.score)}</Badge>
              </div>
              <p className="mt-3 text-sm leading-6 text-neutral-700">{result.text}</p>
            </article>
          ))
        )}
      </div>
    </Card>
  )
}
