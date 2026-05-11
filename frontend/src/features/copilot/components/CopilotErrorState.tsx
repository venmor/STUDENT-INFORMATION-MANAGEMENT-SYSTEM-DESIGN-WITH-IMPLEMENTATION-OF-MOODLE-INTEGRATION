import { Button } from '@/components/ui/Button'

export function CopilotErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900" role="alert" aria-live="assertive">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p>{message}</p>
        <Button variant="secondary" size="sm" className="border-red-300 text-red-800 hover:bg-red-100" onClick={onRetry}>
          Try again
        </Button>
      </div>
    </div>
  )
}
