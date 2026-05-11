import { useState } from 'react'
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'
import { EnhancedDataTable } from '@/components/ui/EnhancedDataTable'
import { Modal } from '@/components/ui/Modal'
import { usePendingRegistrations, usePendingRegistrationMutations } from '@/hooks/useEnrollments'
import { useToast } from '@/hooks/useToast'
import type { Enrollment } from '@/types'

export function AdvisorPendingRegistrationsPage() {
  const [selectedEnrollment, setSelectedEnrollment] = useState<Enrollment | null>(null)
  const [rejectReason, setRejectReason] = useState('')
  const { addToast } = useToast()

  const { data: pending, isLoading } = usePendingRegistrations()
  const { approve, reject } = usePendingRegistrationMutations()

  function handleApprove(enrollment: Enrollment) {
    approve.mutate(enrollment.id, {
      onSuccess: () => {
        addToast('Registration approved', `${enrollment.student_name} enrolled in ${enrollment.section.course_code}.`, 'success')
        setSelectedEnrollment(null)
      },
      onError: () => addToast('Error', 'Failed to approve registration.', 'error'),
    })
  }

  function handleReject() {
    if (!selectedEnrollment) return
    reject.mutate(
      { enrollmentId: selectedEnrollment.id, reason: rejectReason },
      {
        onSuccess: () => {
          addToast('Registration rejected', undefined, 'warning')
          setSelectedEnrollment(null)
          setRejectReason('')
        },
        onError: () => addToast('Error', 'Failed to reject registration.', 'error'),
      },
    )
  }

  const columns = [
    {
      key: 'student_name' as const,
      label: 'Student',
      sortable: true,
    },
    {
      key: 'student_number' as const,
      label: 'Student No.',
      sortable: true,
    },
    {
      key: 'section' as const,
      label: 'Course',
      render: (_: unknown, row: Enrollment) =>
        `${row.section.course_code} — ${row.section.section_code}`,
    },
    {
      key: 'enrolled_at' as const,
      label: 'Requested',
      sortable: true,
      render: (val: string) => new Date(val).toLocaleDateString(),
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-neutral-900">Pending Registrations</h1>
        <p className="mt-1 text-sm text-neutral-500">
          Review and approve student course registration requests.
        </p>
      </div>

      {isLoading ? (
        <p className="text-sm text-neutral-500">Loading...</p>
      ) : (
        <EnhancedDataTable
          data={pending || []}
          columns={columns}
          ariaLabel="Pending registrations"
          actions={(row) => (
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  handleApprove(row)
                }}
                loading={approve.isPending}
              >
                <CheckIcon className="h-4 w-4" />
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedEnrollment(row)
                }}
              >
                <XMarkIcon className="h-4 w-4" />
              </Button>
            </div>
          )}
        />
      )}

      {selectedEnrollment && (
        <Modal
          open={Boolean(selectedEnrollment)}
          onOpenChange={(open) => {
            if (!open) {
              setSelectedEnrollment(null)
              setRejectReason('')
            }
          }}
          title="Reject Registration"
        >
          <div className="space-y-4">
            <p className="text-sm text-neutral-600">
              Rejecting registration for <strong>{selectedEnrollment.student_name}</strong> in{' '}
              <strong>{selectedEnrollment.section.course_code} {selectedEnrollment.section.section_code}</strong>.
            </p>
            <label className="block">
              <span className="text-sm font-medium text-neutral-700">Reason (optional)</span>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                rows={3}
                className="mt-1 block w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="Reason for rejection..."
              />
            </label>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={handleReject}
                loading={reject.isPending}
                className="border-red-300 text-red-700 hover:bg-red-50"
              >
                Confirm Reject
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
