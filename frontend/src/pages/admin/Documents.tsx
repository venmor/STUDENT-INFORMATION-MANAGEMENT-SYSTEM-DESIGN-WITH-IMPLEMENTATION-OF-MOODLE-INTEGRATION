import { useState } from 'react'
import { ArrowPathIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline'

import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { DocumentDetailsPanel } from '@/features/documents/components/DocumentDetailsPanel'
import { DocumentFilters } from '@/features/documents/components/DocumentFilters'
import { DocumentPrivacyNotice } from '@/features/documents/components/DocumentPrivacyNotice'
import { DocumentReviewDialog } from '@/features/documents/components/DocumentReviewDialog'
import { DocumentSummaryCards } from '@/features/documents/components/DocumentSummaryCards'
import { DocumentTable } from '@/features/documents/components/DocumentTable'
import { DocumentUploadDialog } from '@/features/documents/components/DocumentUploadDialog'
import { DocumentWorkflowHealth } from '@/features/documents/components/DocumentWorkflowHealth'
import {
  useApproveDocument,
  useArchiveDocument,
  useDocumentSummary,
  useDocuments,
  useDownloadDocument,
  useRejectDocument,
  useUploadDocument,
} from '@/hooks/useDocuments'
import { useStudents } from '@/hooks/useStudents'
import type { DocumentFilters as DocumentFilterValues, StudentDocument, UploadDocumentPayload } from '@/types/documents'

export function AdminDocumentsPage() {
  const [filters, setFilters] = useState<DocumentFilterValues>({})
  const [selectedDocument, setSelectedDocument] = useState<StudentDocument | null>(null)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [reviewState, setReviewState] = useState<{
    action: 'approve' | 'reject'
    document: StudentDocument
  } | null>(null)

  const documentsQuery = useDocuments(filters)
  const summaryQuery = useDocumentSummary()
  const studentsQuery = useStudents()
  const uploadMutation = useUploadDocument('admin')
  const approveMutation = useApproveDocument()
  const rejectMutation = useRejectDocument()
  const archiveMutation = useArchiveDocument()
  const downloadMutation = useDownloadDocument()

  const documents = documentsQuery.data ?? []

  function refresh() {
    void documentsQuery.refetch()
    void summaryQuery.refetch()
  }

  function upload(payload: UploadDocumentPayload) {
    uploadMutation.mutate(payload, {
      onSuccess: (document) => {
        setUploadOpen(false)
        setSelectedDocument(document)
      },
    })
  }

  function submitReview(reviewNote: string) {
    if (!reviewState) {
      return
    }
    const mutation = reviewState.action === 'approve' ? approveMutation : rejectMutation
    mutation.mutate(
      {
        documentId: reviewState.document.id,
        reviewNote,
      },
      {
        onSuccess: (document) => {
          setReviewState(null)
          setSelectedDocument(document)
        },
      },
    )
  }

  function download(document: StudentDocument) {
    downloadMutation.mutate({ documentId: document.id, fallbackFilename: document.originalFilename })
  }

  return (
    <div className="space-y-6">
      <DocumentSummaryCards summary={summaryQuery.data} isLoading={summaryQuery.isLoading} />
      <DocumentWorkflowHealth summary={summaryQuery.data} />

      {documentsQuery.isError ? (
        <Alert title="Could not load student documents" tone="danger">
          Check the backend API and your admin session.
        </Alert>
      ) : null}

      <Card>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <CardTitle>Document Repository</CardTitle>
            <p className="mt-1 text-sm text-neutral-500">
              Review, classify, and download student-linked institutional documents.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={refresh}>
              <ArrowPathIcon className="h-4 w-4" />
              Refresh
            </Button>
            <Button onClick={() => setUploadOpen(true)}>
              <ArrowUpTrayIcon className="h-4 w-4" />
              Upload Document
            </Button>
          </div>
        </div>

        <div className="mt-5">
          <DocumentFilters filters={filters} onChange={setFilters} showDateRange />
        </div>

        <div className="mt-5 overflow-x-auto">
          <DocumentTable
            documents={documents}
            emptyTitle="No student documents found"
            emptyDescription="Upload a document or seed demo document records to test the workflow."
            isLoading={documentsQuery.isLoading}
            mode="admin"
            onApprove={(document) => setReviewState({ action: 'approve', document })}
            onArchive={(document) => archiveMutation.mutate(document.id)}
            onDownload={download}
            onReject={(document) => setReviewState({ action: 'reject', document })}
            onView={setSelectedDocument}
          />
        </div>
      </Card>

      <DocumentDetailsPanel document={selectedDocument} onDownload={download} />
      <DocumentPrivacyNotice />

      <DocumentUploadDialog
        open={uploadOpen}
        onOpenChange={setUploadOpen}
        onSubmit={upload}
        students={studentsQuery.data ?? []}
        isPending={uploadMutation.isPending}
      />
      <DocumentReviewDialog
        open={Boolean(reviewState)}
        onOpenChange={(open) => {
          if (!open) {
            setReviewState(null)
          }
        }}
        action={reviewState?.action ?? 'approve'}
        document={reviewState?.document}
        onSubmit={submitReview}
        isPending={approveMutation.isPending || rejectMutation.isPending}
      />
    </div>
  )
}
