import { cn } from '@/utils/cn'

const moods = [
  { value: 1, label: 'Very difficult', emoji: '😞' },
  { value: 2, label: 'Difficult', emoji: '😐' },
  { value: 3, label: 'Okay', emoji: '🙂' },
  { value: 4, label: 'Good', emoji: '😊' },
  { value: 5, label: 'Very good', emoji: '😁' },
]

export function MoodSelector({ value, onChange }: { value: number | null; onChange: (v: number) => void }) {
  return (
    <div className="flex justify-between gap-2">
      {moods.map((mood) => (
        <button
          key={mood.value}
          type="button"
          onClick={() => onChange(mood.value)}
          className={cn(
            'flex flex-1 flex-col items-center gap-2 rounded-xl border-2 p-4 transition-all',
            value === mood.value
              ? 'border-wellbeing-accent bg-wellbeing-soft/50 ring-2 ring-wellbeing-accent/20'
              : 'border-neutral-100 hover:border-neutral-200 bg-white',
          )}
        >
          <span className="text-3xl" role="img" aria-label={mood.label}>
            {mood.emoji}
          </span>
          <span className={cn(
            'text-[10px] font-bold uppercase tracking-wider',
            value === mood.value ? 'text-wellbeing-accent' : 'text-neutral-400'
          )}>
            {mood.label}
          </span>
        </button>
      ))}
    </div>
  )
}
