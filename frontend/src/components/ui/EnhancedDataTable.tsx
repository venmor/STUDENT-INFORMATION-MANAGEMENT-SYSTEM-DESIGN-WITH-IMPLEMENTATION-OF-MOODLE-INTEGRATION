import { useMemo, useState, useCallback, type ReactNode } from 'react'
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/24/outline'

import { SearchInput } from '@/components/ui/SearchInput'
import { DataTable, DataTableHead, DataTableHeader, DataTableBody, DataTableRow, DataTableCell, EmptyState } from '@/components/ui/Table'
import { cn } from '@/utils/cn'

export interface Column<T> {
  key: keyof T & string
  label: string
  sortable?: boolean
  filterable?: boolean
  filterOptions?: { label: string; value: string }[]
  render?: (value: T[keyof T], row: T) => ReactNode
}

interface EnhancedDataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  ariaLabel: string
  searchableKeys?: (keyof T & string)[]
  actions?: (row: T) => ReactNode
  onRowClick?: (row: T) => void
  emptyTitle?: string
  emptyDescription?: string
}

type SortDirection = 'asc' | 'desc'

export function EnhancedDataTable<T extends { id?: string }>({
  data,
  columns,
  ariaLabel,
  searchableKeys,
  actions,
  onRowClick,
  emptyTitle = 'No data found',
  emptyDescription = 'Try adjusting your search or filters.',
}: EnhancedDataTableProps<T>) {
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState<(keyof T & string) | null>(null)
  const [sortDir, setSortDir] = useState<SortDirection>('asc')
  const [filters, setFilters] = useState<Record<string, string>>({})

  const handleSort = useCallback((key: keyof T & string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }, [sortKey])

  const searchKeys = searchableKeys ?? columns.map((c) => c.key)

  const filtered = useMemo(() => {
    let result = data

    if (search) {
      const lower = search.toLowerCase()
      result = result.filter((row) =>
        searchKeys.some((key) => String(row[key] ?? '').toLowerCase().includes(lower)),
      )
    }

    for (const [key, value] of Object.entries(filters)) {
      if (value) {
        result = result.filter((row) => String(row[key as keyof T] ?? '') === value)
      }
    }

    if (sortKey) {
      result = [...result].sort((a, b) => {
        const aVal = String(a[sortKey] ?? '')
        const bVal = String(b[sortKey] ?? '')
        const cmp = aVal.localeCompare(bVal, undefined, { numeric: true })
        return sortDir === 'asc' ? cmp : -cmp
      })
    }

    return result
  }, [data, search, filters, sortKey, sortDir, searchKeys])

  const filterableColumns = columns.filter((c) => c.filterable && c.filterOptions)

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <SearchInput value={search} onChange={setSearch} placeholder="Search..." className="w-64" />
        {filterableColumns.map((col) => (
          <select
            key={col.key}
            value={filters[col.key] ?? ''}
            onChange={(e) => setFilters((f) => ({ ...f, [col.key]: e.target.value }))}
            className="rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-700 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
          >
            <option value="">{col.label} (All)</option>
            {col.filterOptions!.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        ))}
      </div>

      {filtered.length === 0 ? (
        <EmptyState title={emptyTitle} description={emptyDescription} />
      ) : (
        <DataTable ariaLabel={ariaLabel}>
          <DataTableHead>
            <tr>
              {columns.map((col) => (
                <DataTableHeader key={col.key}>
                  {col.sortable ? (
                    <button
                      type="button"
                      onClick={() => handleSort(col.key)}
                      className="inline-flex items-center gap-1 font-medium uppercase tracking-wider hover:text-neutral-700"
                    >
                      {col.label}
                      <span className="inline-flex flex-col">
                        <ChevronUpIcon className={cn('h-3 w-3', sortKey === col.key && sortDir === 'asc' ? 'text-primary' : 'text-neutral-300')} />
                        <ChevronDownIcon className={cn('-mt-1 h-3 w-3', sortKey === col.key && sortDir === 'desc' ? 'text-primary' : 'text-neutral-300')} />
                      </span>
                    </button>
                  ) : (
                    col.label
                  )}
                </DataTableHeader>
              ))}
              {actions && <DataTableHeader>Actions</DataTableHeader>}
            </tr>
          </DataTableHead>
          <DataTableBody>
            {filtered.map((row, i) => (
              <DataTableRow
                key={(row as Record<string, unknown>).id as string ?? i}
                className={onRowClick ? 'cursor-pointer' : undefined}
              >
                {columns.map((col) => (
                  <DataTableCell key={col.key} onClick={onRowClick ? () => onRowClick(row) : undefined}>
                    {col.render ? col.render(row[col.key], row) : String(row[col.key] ?? '')}
                  </DataTableCell>
                ))}
                {actions && <DataTableCell>{actions(row)}</DataTableCell>}
              </DataTableRow>
            ))}
          </DataTableBody>
        </DataTable>
      )}
    </div>
  )
}
