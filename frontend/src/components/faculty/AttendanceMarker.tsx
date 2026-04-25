import { Button } from '@/components/ui/Button'

export function AttendanceMarker({
  onSelect,
}: {
  onSelect: (status: 'PRESENT' | 'ABSENT' | 'EXCUSED') => void
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <Button variant="secondary" size="sm" onClick={() => onSelect('PRESENT')}>
        Present
      </Button>
      <Button variant="ghost" size="sm" onClick={() => onSelect('ABSENT')}>
        Absent
      </Button>
      <Button variant="ghost" size="sm" onClick={() => onSelect('EXCUSED')}>
        Excused
      </Button>
    </div>
  )
}
