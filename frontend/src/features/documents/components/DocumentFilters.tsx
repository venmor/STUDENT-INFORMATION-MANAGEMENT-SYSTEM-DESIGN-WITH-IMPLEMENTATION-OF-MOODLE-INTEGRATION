import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import type { DocumentFilters } from '@/types/documents'
import { documentStatusOptions, documentTypeOptions, documentVisibilityOptions } from '@/features/documents/utils/documentLabels'

const allItem = { label: 'All', value: 'ALL' }

export function DocumentFilters({
  filters,
  onChange,
  showDateRange = false,
  showVisibility = true,
}: {
  filters: DocumentFilters
  onChange: (filters: DocumentFilters) => void
  showDateRange?: boolean
  showVisibility?: boolean
}) {
  function update(next: Partial<DocumentFilters>) {
    onChange({ ...filters, ...next })
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
      <Input
        id="document-search"
        label="Search"
        placeholder="Search student, document title, filename, or type"
        value={filters.search ?? ''}
        onChange={(event) => update({ search: event.target.value })}
      />
      <Select
        id="document-type-filter"
        label="Document type"
        value={filters.documentType ?? 'ALL'}
        onValueChange={(value) => update({ documentType: value })}
        items={[allItem, ...documentTypeOptions]}
      />
      <Select
        id="document-status-filter"
        label="Status"
        value={filters.status ?? 'ALL'}
        onValueChange={(value) => update({ status: value })}
        items={[allItem, ...documentStatusOptions]}
      />
      {showVisibility ? (
        <Select
          id="document-visibility-filter"
          label="Visibility"
          value={filters.visibility ?? 'ALL'}
          onValueChange={(value) => update({ visibility: value })}
          items={[allItem, ...documentVisibilityOptions]}
        />
      ) : null}
      {showDateRange ? (
        <>
          <Input
            id="document-date-from"
            label="Date from"
            type="date"
            value={filters.dateFrom ?? ''}
            onChange={(event) => update({ dateFrom: event.target.value })}
          />
          <Input
            id="document-date-to"
            label="Date to"
            type="date"
            value={filters.dateTo ?? ''}
            onChange={(event) => update({ dateTo: event.target.value })}
          />
        </>
      ) : null}
    </div>
  )
}
