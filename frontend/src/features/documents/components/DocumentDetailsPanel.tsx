import { ArrowDownTrayIcon } from '@heroicons/react/24/outline'

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { EmptyState } from '@/components/ui/EmptyState'
import { formatDocumentDate, formatFileSize } from '@/features/documents/utils/documentFormatting'
import {
  documentStatusLabel,
  documentStatusTone,
  documentTypeLabel,
  documentVisibilityLabel,
  documentVisibilityTone,
} from '@/features/documents/utils/documentLabels'
import type { StudentDocument } from '@/types/documents'

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-neutral-500">{label}</dt>
      <dd className="mt-1 break-words text-sm text-neutral-900">{value || 'Not recorded'}</dd>
    </div>
  )
}

export function DocumentDetailsPanel({
  document,
  onDownload,
}: {
  document?: StudentDocument | null
  onDownload: (document: StudentDocument) => void
}) {
  if (!document) {
    return (
      <EmptyState
        title="Select a document"
        description="Choose a row to review document metadata, visibility, status, and audit-safe details."
      />
    )
  }

  return (
    <Card className="p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <CardTitle>Document Details</CardTitle>
          <p className="mt-1 text-sm text-neutral-500">{document.title}</p>
        </div>
        {document.canDownload ? (
          <Button variant="secondary" size="sm" onClick={() => onDownload(document)}>
            <ArrowDownTrayIcon className="h-4 w-4" />
            Download
          </Button>
        ) : null}
      </div>

      <dl className="mt-5 grid gap-4 sm:grid-cols-2">
        <DetailRow label="Student" value={`${document.student.fullName} (${document.student.studentNumber})`} />
        <DetailRow label="Programme" value={document.student.programme} />
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-neutral-500">Type</dt>
          <dd className="mt-1 text-sm text-neutral-900">{documentTypeLabel(document.documentType)}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-neutral-500">Visibility</dt>
          <dd className="mt-1">
            <Badge tone={documentVisibilityTone(document.visibility)}>{documentVisibilityLabel(document.visibility)}</Badge>
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-neutral-500">Status</dt>
          <dd className="mt-1">
            <Badge tone={documentStatusTone(document.status)}>{documentStatusLabel(document.status)}</Badge>
          </dd>
        </div>
        <DetailRow label="Filename" value={document.originalFilename} />
        <DetailRow label="Content type" value={document.contentType} />
        <DetailRow label="File size" value={formatFileSize(document.fileSize)} />
        <DetailRow label="Uploaded by" value={document.uploadedBy?.fullName ?? 'System'} />
        <DetailRow label="Uploaded date" value={formatDocumentDate(document.createdAt)} />
        <DetailRow label="Reviewed by" value={document.reviewedBy?.fullName ?? ''} />
        <DetailRow label="Reviewed date" value={formatDocumentDate(document.reviewedAt)} />
      </dl>

      {document.description ? (
        <div className="mt-5">
          <h4 className="text-sm font-semibold text-neutral-900">Description</h4>
          <p className="mt-1 text-sm leading-6 text-neutral-600">{document.description}</p>
        </div>
      ) : null}

      {document.reviewNote ? (
        <div className="mt-5 rounded-lg border border-neutral-200 bg-neutral-50 p-3">
          <h4 className="text-sm font-semibold text-neutral-900">Review Note</h4>
          <p className="mt-1 text-sm leading-6 text-neutral-600">{document.reviewNote}</p>
        </div>
      ) : null}

      <div className="mt-5">
        <h4 className="text-sm font-semibold text-neutral-900">Audit-Safe Metadata</h4>
        <pre className="mt-2 max-h-48 overflow-auto rounded-lg bg-neutral-950 p-3 text-xs text-neutral-100">
          {JSON.stringify(document.metadata ?? {}, null, 2)}
        </pre>
      </div>
    </Card>
  )
}
