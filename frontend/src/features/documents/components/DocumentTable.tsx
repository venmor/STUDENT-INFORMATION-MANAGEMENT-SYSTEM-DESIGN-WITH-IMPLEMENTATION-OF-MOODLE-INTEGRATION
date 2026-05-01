import { ArrowDownTrayIcon, ArchiveBoxIcon, CheckCircleIcon, EyeIcon, XCircleIcon } from '@heroicons/react/24/outline'

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { EmptyState } from '@/components/ui/EmptyState'
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHead,
  DataTableHeader,
  DataTableRow,
  TableSkeleton,
} from '@/components/ui/Table'
import { formatDocumentDate, formatFileSize } from '@/features/documents/utils/documentFormatting'
import {
  documentStatusLabel,
  documentStatusTone,
  documentTypeLabel,
  documentVisibilityLabel,
  documentVisibilityTone,
} from '@/features/documents/utils/documentLabels'
import type { StudentDocument } from '@/types/documents'
import { cn } from '@/utils/cn'

export function DocumentTable({
  documents,
  emptyDescription,
  emptyTitle,
  isLoading,
  mode = 'admin',
  onApprove,
  onArchive,
  onDownload,
  onReject,
  onView,
}: {
  documents: StudentDocument[]
  emptyDescription: string
  emptyTitle: string
  isLoading?: boolean
  mode?: 'admin' | 'student'
  onApprove?: (document: StudentDocument) => void
  onArchive?: (document: StudentDocument) => void
  onDownload: (document: StudentDocument) => void
  onReject?: (document: StudentDocument) => void
  onView: (document: StudentDocument) => void
}) {
  if (isLoading) {
    return <TableSkeleton columns={mode === 'admin' ? 9 : 6} />
  }

  if (documents.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />
  }

  return (
    <DataTable ariaLabel={mode === 'admin' ? 'Student document repository' : 'My student documents'}>
      <DataTableHead>
        <DataTableRow>
          {mode === 'admin' ? <DataTableHeader>Student</DataTableHeader> : null}
          <DataTableHeader>Document</DataTableHeader>
          <DataTableHeader>Type</DataTableHeader>
          {mode === 'admin' ? <DataTableHeader>Visibility</DataTableHeader> : null}
          <DataTableHeader>Status</DataTableHeader>
          {mode === 'admin' ? <DataTableHeader>Uploaded By</DataTableHeader> : null}
          <DataTableHeader>Uploaded Date</DataTableHeader>
          <DataTableHeader>File</DataTableHeader>
          <DataTableHeader className="min-w-[18rem]">Actions</DataTableHeader>
        </DataTableRow>
      </DataTableHead>
      <DataTableBody>
        {documents.map((document) => (
          <DataTableRow key={document.id} className={cn(document.status === 'ARCHIVED' && 'opacity-70')}>
            {mode === 'admin' ? (
              <DataTableCell>
                <div className="font-medium">{document.student.fullName}</div>
                <div className="mt-1 text-xs text-neutral-500">{document.student.studentNumber}</div>
              </DataTableCell>
            ) : null}
            <DataTableCell>
              <div className="max-w-xs truncate font-medium" title={document.title}>
                {document.title}
              </div>
              {document.description ? (
                <div className="mt-1 max-w-xs truncate text-xs text-neutral-500" title={document.description}>
                  {document.description}
                </div>
              ) : null}
            </DataTableCell>
            <DataTableCell>{documentTypeLabel(document.documentType)}</DataTableCell>
            {mode === 'admin' ? (
              <DataTableCell>
                <Badge tone={documentVisibilityTone(document.visibility)}>{documentVisibilityLabel(document.visibility)}</Badge>
              </DataTableCell>
            ) : null}
            <DataTableCell>
              <Badge tone={documentStatusTone(document.status)}>{documentStatusLabel(document.status)}</Badge>
              {document.status === 'REJECTED' && document.reviewNote ? (
                <p className="mt-1 text-xs text-neutral-500">Review note available</p>
              ) : null}
            </DataTableCell>
            {mode === 'admin' ? (
              <DataTableCell>{document.uploadedBy?.fullName ?? 'System'}</DataTableCell>
            ) : null}
            <DataTableCell>{formatDocumentDate(document.createdAt)}</DataTableCell>
            <DataTableCell>
              <span className="block max-w-[12rem] truncate" title={document.originalFilename}>
                {document.originalFilename}
              </span>
              <span className="mt-1 block text-xs text-neutral-500">{formatFileSize(document.fileSize)}</span>
            </DataTableCell>
            <DataTableCell>
              <div className="flex flex-wrap gap-2">
                <Button variant="secondary" size="sm" onClick={() => onView(document)}>
                  <EyeIcon className="h-4 w-4" />
                  View Details
                </Button>
                {document.canDownload ? (
                  <Button variant="secondary" size="sm" onClick={() => onDownload(document)}>
                    <ArrowDownTrayIcon className="h-4 w-4" />
                    Download
                  </Button>
                ) : null}
                {document.canReview && onApprove ? (
                  <Button variant="secondary" size="sm" onClick={() => onApprove(document)}>
                    <CheckCircleIcon className="h-4 w-4" />
                    Approve
                  </Button>
                ) : null}
                {document.canReview && onReject ? (
                  <Button variant="secondary" size="sm" onClick={() => onReject(document)}>
                    <XCircleIcon className="h-4 w-4" />
                    Reject
                  </Button>
                ) : null}
                {document.canArchive && onArchive && document.status !== 'ARCHIVED' ? (
                  <Button variant="ghost" size="sm" onClick={() => onArchive(document)}>
                    <ArchiveBoxIcon className="h-4 w-4" />
                    Archive
                  </Button>
                ) : null}
              </div>
            </DataTableCell>
          </DataTableRow>
        ))}
      </DataTableBody>
    </DataTable>
  )
}
