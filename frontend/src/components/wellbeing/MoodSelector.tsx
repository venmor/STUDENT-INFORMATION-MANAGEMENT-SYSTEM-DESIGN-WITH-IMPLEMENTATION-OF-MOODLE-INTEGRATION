const moods = [
  { label: '1 — Very difficult', value: 1 },
  { label: '2 — Difficult', value: 2 },
  { label: '3 — Okay', value: 3 },
  { label: '4 — Good', value: 4 },
  { label: '5 — Doing well', value: 5 },
]

export function MoodSelector({
  onChange,
  value,
}: {
  onChange: (value: number) => void
  value?: number
}) {
  return (
    <div className="space-y-3">
      {moods.map((mood) => (
        <button
          key={mood.value}
          type="button"
          className={
            value === mood.value
              ? 'w-full rounded-xl border-2 border-wellbeing-accent bg-wellbeing-muted px-4 py-4 text-left font-semibold text-wellbeing-accent'
              : 'w-full rounded-xl border-2 border-neutral-200 bg-white px-4 py-4 text-left text-neutral-700 hover:border-wellbeing-accent/50'
          }
          onClick={() => onChange(mood.value)}
        >
          {mood.label}
        </button>
      ))}
    </div>
  )
}
