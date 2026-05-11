import { useState } from 'react'
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'
import { EnhancedDataTable } from '@/components/ui/EnhancedDataTable'
import { Modal } from '@/components/ui/Modal'
import { useApplications, useApproveApplication, useRejectApplication } from '@/hooks/useAdmissions'
import { useToast } from '@/hooks/useToast'
import type { ApplicantProfile, ApplicationStatus } from '@/types/admissions'

const STATUS_COLORS: Record<ApplicationStatus, string> = {
  DRAFT: 'bg-neutral-100 text-neutral-700',
  SUBMITTED: 'bg-blue-100 text-blue-700',
  UNDER_REVIEW: 'bg-yellow-100 text-yellow-700',
  ACCEPTED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
  WAITLISTED: 'bg-purple-100 text-purple-700',
}

export function AdminAdmissionsPage() {
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [selectedApplicant, setSelectedApplicant] = useState<ApplicantProfile | null>(null)
  const [reviewNotes, setReviewNotes] = useState('')
  const { addToast } = useToast()

  const { data: applications, isLoading } = useApplications(
    statusFilter ? { status: statusFilter } : undefined,
  )
  const approveApp = useApproveApplication()
  const rejectApp = useRejectApplication()

  function handleApprove() {
    if (!selectedApplicant) return
    approveApp.mutate(
      { applicantId: selectedApplicant.id, reviewNotes },
      {
        onSuccess: () => {
          addToast('Application approved', 'Student account has been created.', 'success')
          setSelectedApplicant(null)
          setReviewNotes('')
        },
        onError: () => addToast('Error', 'Failed to approve application.', 'error'),
      },
    )
  }

  function handleReject() {
    if (!selectedApplicant) return
    rejectApp.mutate(
      { applicantId: selectedApplicant.id, reviewNotes },
      {
        onSuccess: () => {
          addToast('Application rejected', undefined, 'warning')
          setSelectedApplicant(null)
          setReviewNotes('')
        },
        onError: () => addToast('Error', 'Failed to reject application.', 'error'),
      },
    )
  }

  const columns = [
    {
      key: 'fullName' as const,
      label: 'Applicant',
      sortable: true,
    },
    {
      key: 'email' as const,
      label: 'Email',
      sortable: true,
    },
    {
      key: 'programmeName' as const,
      label: 'Programme',
      sortable: true,
      render: (val: string | null) => val || '—',
    },
    {
      key: 'applicationStatus' as const,
      label: 'Status',
      filterable: true,
      filterOptions: [
        { value: 'SUBMITTED', label: 'Submitted' },
        { value: 'UNDER_REVIEW', label: 'Under Review' },
        { value: 'ACCEPTED', label: 'Accepted' },
        { value: 'REJECTED', label: 'Rejected' },
        { value: 'WAITLISTED', label: 'Waitlisted' },
      ],
      render: (val: ApplicationStatus) => (
        <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[val]}`}>
          {val.replace('_', ' ')}
        </span>
      ),
    },
    {
      key: 'createdAt' as const,
      label: 'Applied',
      sortable: true,
      render: (val: string) => new Date(val).toLocaleDateString(),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-neutral-900">Admissions</h1>
          <p className="mt-1 text-sm text-neutral-500">Review and process student applications</p>
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-neutral-300 px-3 py-2 text-sm"
        >
          <option value="">All statuses</option>
          <option value="SUBMITTED">Submitted</option>
          <option value="UNDER_REVIEW">Under Review</option>
          <option value="ACCEPTED">Accepted</option>
          <option value="REJECTED">Rejected</option>
          <option value="WAITLISTED">Waitlisted</option>
        </select>
      </div>

      {isLoading ? (
        <p className="text-sm text-neutral-500">Loading applications...</p>
      ) : (
        <EnhancedDataTable
          data={applications || []}
          columns={columns}
          ariaLabel="Admissions applications"
          onRowClick={(app) => setSelectedApplicant(app)}
        />
      )}

      {selectedApplicant && (
        <Modal
          open={Boolean(selectedApplicant)}
          onOpenChange={(open) => {
            if (!open) {
              setSelectedApplicant(null)
              setReviewNotes('')
            }
          }}
          title={`Application: ${selectedApplicant.fullName}`}
        >
          <div className="space-y-4">
            <div className="grid gap-3 text-sm sm:grid-cols-2">
              <div><span className="font-medium text-neutral-500">Email:</span> {selectedApplicant.email}</div>
              <div><span className="font-medium text-neutral-500">Phone:</span> {selectedApplicant.phoneNumber}</div>
              <div><span className="font-medium text-neutral-500">National ID:</span> {selectedApplicant.nationalId}</div>
              <div><span className="font-medium text-neutral-500">DOB:</span> {selectedApplicant.dateOfBirth}</div>
              <div><span className="font-medium text-neutral-500">Gender:</span> {selectedApplicant.gender}</div>
              <div><span className="font-medium text-neutral-500">Programme:</span> {selectedApplicant.programmeName || '—'}</div>
            </div>

            <div>
              <p className="text-sm font-medium text-neutral-700">
                Status:{' '}
                <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[selectedApplicant.applicationStatus]}`}>
                  {selectedApplicant.applicationStatus.replace('_', ' ')}
                </span>
              </p>
            </div>

            {selectedApplicant.documents.length > 0 && (
              <div>
                <p className="text-sm font-medium text-neutral-700">Documents:</p>
                <ul className="mt-1 space-y-1">
                  {selectedApplicant.documents.map((doc) => (
                    <li key={doc.id} className="text-sm text-neutral-600">
                      {doc.documentType} — {doc.originalFilename}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {(selectedApplicant.applicationStatus === 'SUBMITTED' ||
              selectedApplicant.applicationStatus === 'UNDER_REVIEW') && (
              <div className="space-y-3 border-t border-neutral-200 pt-4">
                <label className="block">
                  <span className="text-sm font-medium text-neutral-700">Review Notes</span>
                  <textarea
                    value={reviewNotes}
                    onChange={(e) => setReviewNotes(e.target.value)}
                    rows={3}
                    className="mt-1 block w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                    placeholder="Optional review notes..."
                  />
                </label>
                <div className="flex gap-3">
                  <Button
                    onClick={handleApprove}
                    loading={approveApp.isPending}
                    className="flex items-center gap-1"
                  >
                    <CheckIcon className="h-4 w-4" />
                    Approve
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleReject}
                    loading={rejectApp.isPending}
                    className="flex items-center gap-1 border-red-300 text-red-700 hover:bg-red-50"
                  >
                    <XMarkIcon className="h-4 w-4" />
                    Reject
                  </Button>
                </div>
              </div>
            )}

            {selectedApplicant.reviewNotes && (
              <div className="border-t border-neutral-200 pt-3">
                <p className="text-sm font-medium text-neutral-700">Review Notes:</p>
                <p className="mt-1 text-sm text-neutral-600">{selectedApplicant.reviewNotes}</p>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  )
}
