import type { ReactNode } from 'react'

import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn } from '@/utils/cn'

export function DataTable({
  ariaLabel,
  children,
  className,
}: {
  ariaLabel: string
  children: ReactNode
  className?: string
}) {
  return (
    <div className={cn('overflow-x-auto rounded-lg border border-neutral-200 bg-white', className)}>
      <table aria-label={ariaLabel} className="min-w-full divide-y divide-neutral-200">
        {children}
      </table>
    </div>
  )
}

export function DataTableHead({ children }: { children: ReactNode }) {
  return <thead className="bg-neutral-50">{children}</thead>
}

export function DataTableHeader({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <th
      scope="col"
      className={cn(
        'px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-neutral-500',
        className,
      )}
    >
      {children}
    </th>
  )
}

export function DataTableBody({ children }: { children: ReactNode }) {
  return <tbody className="divide-y divide-neutral-100">{children}</tbody>
}

export function DataTableRow({ children, className }: { children: ReactNode; className?: string }) {
  return <tr className={cn('even:bg-neutral-50/50 hover:bg-neutral-50', className)}>{children}</tr>
}

export function DataTableCell({ children, className }: { children: ReactNode; className?: string }) {
  return <td className={cn('px-4 py-3 text-sm text-neutral-900', className)}>{children}</td>
}

export function TableSkeleton({ columns, rows = 5 }: { columns: number; rows?: number }) {
  return (
    <DataTable ariaLabel="Loading table">
      <DataTableBody>
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <DataTableRow key={rowIndex}>
            {Array.from({ length: columns }).map((__, columnIndex) => (
              <DataTableCell key={columnIndex}>
                <Skeleton className="h-4 w-full" />
              </DataTableCell>
            ))}
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}

export { EmptyState }
