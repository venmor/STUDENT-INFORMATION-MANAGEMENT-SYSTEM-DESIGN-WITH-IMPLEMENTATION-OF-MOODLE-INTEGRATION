import { useState } from 'react'
import { ArrowPathIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline'

import { Alert } from '@/components/ui/Alert'
import { Button } from '@/components/ui/Button'
import { Card, CardTitle } from '@/components/ui/Card'
import { DocumentDetailsPanel } from '@/features/documents/components/DocumentDetailsPanel'
import { DocumentFilters } from '@/features/documents/components/DocumentFilters'
import { DocumentPrivacyNotice } from '@/features/documents/components/DocumentPrivacyNotice'
import { DocumentSummaryCards } from '@/features/documents/components/DocumentSummaryCards'
import { DocumentTable } from '@/features/documents/components/DocumentTable'
import { DocumentUploadDialog } from '@/features/documents/components/DocumentUploadDialog'
import { useDocumentSummary, useDownloadDocument, useMyDocuments, useUploadDocument } from '@/hooks/useDocuments'
import type { DocumentFilters as DocumentFilterValues, StudentDocument, UploadDocumentPayload } from '@/types/documents'

export function StudentDocumentsPage() {
  const [filters, setFilters] = useState<DocumentFilterValues>({})
  const [selectedDocument, setSelectedDocument] = useState<StudentDocument | null>(null)
  const [uploadOpen, setUploadOpen] = useState(false)

  const documentsQuery = useMyDocuments(filters)
  const summaryQuery = useDocumentSummary()
  const uploadMutation = useUploadDocument('student')
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

  function download(document: StudentDocument) {
    downloadMutation.mutate({ documentId: document.id, fallbackFilename: document.originalFilename })
  }

  return (
    <div className="space-y-6">
      <DocumentSummaryCards context="student" summary={summaryQuery.data} isLoading={summaryQuery.isLoading} />

      {documentsQuery.isError ? (
        <Alert title="Could not load student documents" tone="danger">
          Check the backend API and your student session.
        </Alert>
      ) : null}

      <Card>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <CardTitle>My Documents</CardTitle>
            <p className="mt-1 text-sm text-neutral-500">
              Documents shared with you by the institution and supporting files you have uploaded.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={refresh}>
              <ArrowPathIcon className="h-4 w-4" />
              Refresh
            </Button>
            <Button onClick={() => setUploadOpen(true)}>
              <ArrowUpTrayIcon className="h-4 w-4" />
              Upload Supporting Document
            </Button>
          </div>
        </div>

        <div className="mt-5">
          <DocumentFilters filters={filters} onChange={setFilters} showVisibility={false} />
        </div>

        <div className="mt-5 overflow-x-auto">
          <DocumentTable
            documents={documents}
            emptyTitle="No documents have been shared with you yet."
            emptyDescription="Institution-shared records and your uploaded supporting files will appear here."
            isLoading={documentsQuery.isLoading}
            mode="student"
            onDownload={download}
            onView={setSelectedDocument}
          />
        </div>
      </Card>

      <DocumentDetailsPanel document={selectedDocument} onDownload={download} />
      <DocumentPrivacyNotice studentUploadEnabled />

      <DocumentUploadDialog
        open={uploadOpen}
        onOpenChange={setUploadOpen}
        onSubmit={upload}
        mode="student"
        isPending={uploadMutation.isPending}
      />
    </div>
  )
}
