import { Card } from '@/components/ui/Card'

export function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="max-w-lg text-center">
        <h1 className="text-2xl font-semibold text-neutral-900">Page not found</h1>
        <p className="mt-2 text-sm text-neutral-500">
          The requested route does not exist in the current Student Information System frontend.
        </p>
      </Card>
    </div>
  )
}
