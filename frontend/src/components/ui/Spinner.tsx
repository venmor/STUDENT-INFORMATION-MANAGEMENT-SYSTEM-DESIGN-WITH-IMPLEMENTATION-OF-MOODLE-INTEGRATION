import { cn } from '@/utils/cn'

const sizes = {
  sm: 'h-4 w-4 border-2',
  md: 'h-5 w-5 border-2',
  lg: 'h-6 w-6 border-[3px]',
} as const

export function Spinner({
  size = 'md',
  className,
}: {
  size?: keyof typeof sizes
  className?: string
}) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        'inline-block animate-spin rounded-full border-current border-r-transparent',
        sizes[size],
        className,
      )}
    />
  )
}
