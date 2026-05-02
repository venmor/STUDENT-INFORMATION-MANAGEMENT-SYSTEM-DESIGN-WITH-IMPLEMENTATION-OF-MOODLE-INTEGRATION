const examples = [
  'What is the deadline to drop a course?',
  'How do I register for courses?',
  'Where can I see my official grades?',
  'What should I do if my document was rejected?',
  'Show me important academic deadlines.',
  'How do I contact the Registrar?',
]

export function CopilotExamplePrompts({ onSelect }: { onSelect: (prompt: string) => void }) {
  return (
    <div className="grid gap-2 sm:grid-cols-2">
      {examples.map((prompt) => (
        <button
          key={prompt}
          type="button"
          className="min-h-11 rounded-lg border border-neutral-200 bg-white px-3 py-2 text-left text-sm font-medium text-neutral-700 transition-colors hover:border-primary/30 hover:bg-primary-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
          onClick={() => onSelect(prompt)}
        >
          {prompt}
        </button>
      ))}
    </div>
  )
}
