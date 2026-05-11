export function CopilotThinkingIndicator({ label }: { label: string }) {
  return (
    <div
      className="mr-auto max-w-[82%] rounded-lg rounded-bl-sm border border-neutral-200 bg-neutral-50 px-4 py-3 text-sm text-neutral-700"
      aria-live="polite"
    >
      <span className="font-medium">{label}</span>
    </div>
  )
}
