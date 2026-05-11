import { useState } from 'react'
import { CheckCircleIcon, DocumentArrowUpIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'
import { useCreateApplication, useSubmitApplication, useUploadApplicantDocument } from '@/hooks/useAdmissions'
import { useProgrammes } from '@/hooks/useStructure'
import type { ApplicantDocumentType } from '@/types/admissions'

type Step = 'personal' | 'programme' | 'documents' | 'review' | 'submitted'

const DOCUMENT_TYPES: { value: ApplicantDocumentType; label: string }[] = [
  { value: 'TRANSCRIPT', label: 'Transcript' },
  { value: 'NATIONAL_ID', label: 'National ID' },
  { value: 'BIRTH_CERTIFICATE', label: 'Birth Certificate' },
  { value: 'PASSPORT_PHOTO', label: 'Passport Photo' },
  { value: 'OTHER', label: 'Other' },
]

const STEPS: { key: Step; label: string }[] = [
  { key: 'personal', label: 'Personal Info' },
  { key: 'programme', label: 'Programme' },
  { key: 'documents', label: 'Documents' },
  { key: 'review', label: 'Review & Submit' },
]

export function ApplyPage() {
  const [step, setStep] = useState<Step>('personal')
  const [applicantId, setApplicantId] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    national_id: '',
    date_of_birth: '',
    gender: '',
    phone_number: '',
    programme_applied: null as string | null,
  })
  const [uploadedDocs, setUploadedDocs] = useState<{ type: ApplicantDocumentType; name: string }[]>([])
  const [error, setError] = useState<string | null>(null)

  const createApp = useCreateApplication()
  const uploadDoc = useUploadApplicantDocument()
  const submitApp = useSubmitApplication()
  const { data: programmes } = useProgrammes()

  const currentStepIndex = STEPS.findIndex((s) => s.key === step)

  function handlePersonalSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setStep('programme')
  }

  function handleProgrammeSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    createApp.mutate(formData, {
      onSuccess: (data) => {
        setApplicantId(data.id)
        setStep('documents')
      },
      onError: (err: unknown) => {
        const msg = (err as { response?: { data?: Record<string, string[]> } })?.response?.data
        if (msg) {
          const firstField = Object.keys(msg)[0]
          setError(`${firstField}: ${msg[firstField][0]}`)
        } else {
          setError('Failed to create application. Please try again.')
        }
      },
    })
  }

  async function handleFileUpload(docType: ApplicantDocumentType, file: File) {
    if (!applicantId) return
    setError(null)
    uploadDoc.mutate(
      { applicantId, documentType: docType, file },
      {
        onSuccess: () => {
          setUploadedDocs((prev) => [...prev, { type: docType, name: file.name }])
        },
        onError: () => setError('Failed to upload document. Please try again.'),
      },
    )
  }

  function handleSubmit() {
    if (!applicantId) return
    setError(null)
    submitApp.mutate(applicantId, {
      onSuccess: () => setStep('submitted'),
      onError: () => setError('Failed to submit application. Please try again.'),
    })
  }

  if (step === 'submitted') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-neutral-50 px-4">
        <div className="w-full max-w-md rounded-2xl border border-neutral-200 bg-white p-8 text-center shadow-card">
          <CheckCircleIcon className="mx-auto h-16 w-16 text-green-500" />
          <h1 className="mt-4 font-display text-2xl font-bold text-neutral-900">Application Submitted</h1>
          <p className="mt-2 text-sm text-neutral-600">
            Your application has been received and is under review. You will be contacted via email with the outcome.
          </p>
          <a href="/login" className="mt-6 inline-block text-sm font-medium text-primary hover:underline">
            Back to Login
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-neutral-50 py-10 px-4">
      <div className="mx-auto max-w-2xl">
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-3">
            <img src="/sis-logo.svg" alt="" className="h-10 w-10" />
            <h1 className="font-display text-2xl font-bold text-neutral-900">Student Admission Application</h1>
          </div>
        </div>

        <div className="mb-8 flex items-center justify-center gap-2">
          {STEPS.map((s, idx) => (
            <div key={s.key} className="flex items-center gap-2">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                  idx <= currentStepIndex
                    ? 'bg-primary text-white'
                    : 'bg-neutral-200 text-neutral-500'
                }`}
              >
                {idx + 1}
              </div>
              <span className="hidden text-sm font-medium text-neutral-700 sm:inline">{s.label}</span>
              {idx < STEPS.length - 1 && <div className="h-px w-8 bg-neutral-300" />}
            </div>
          ))}
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="rounded-2xl border border-neutral-200 bg-white p-8 shadow-card">
          {step === 'personal' && (
            <form onSubmit={handlePersonalSubmit} className="space-y-4">
              <h2 className="font-display text-lg font-bold text-neutral-900">Personal Information</h2>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block">
                  <span className="text-sm font-medium text-neutral-700">Full Name *</span>
                  <input
                    type="text"
                    required
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                    className="mt-1 block w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </label>
                <label className="block">
                  <span className="text-sm font-medium text-neutral-700">Email *</span>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="mt-1 block w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </label>
                <label className="block">
                  <span className="text-sm font-medium text-neutral-700">National ID *</span>
                  <input
                    type="text"
                    required
                    value={formData.national_id}
                    onChange={(e) => setFormData({ ...formData, national_id: e.target.value })}
                    className="mt-1 block w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </label>
                <label className="block">
                  <span className="text-sm font-medium text-neutral-700">Date of Birth *</span>
                  <input
                    type="date"
                    required
                    value={formData.date_of_birth}
                    onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                    className="mt-1 block w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </label>
                <label className="block">
                  <span className="text-sm font-medium text-neutral-700">Gender *</span>
                  <select
                    required
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                    className="mt-1 block w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="">Select...</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </label>
                <label className="block">
                  <span className="text-sm font-medium text-neutral-700">Phone Number *</span>
                  <input
                    type="tel"
                    required
                    value={formData.phone_number}
                    onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                    className="mt-1 block w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </label>
              </div>
              <div className="flex justify-end pt-4">
                <Button type="submit">Next: Programme</Button>
              </div>
            </form>
          )}

          {step === 'programme' && (
            <form onSubmit={handleProgrammeSubmit} className="space-y-4">
              <h2 className="font-display text-lg font-bold text-neutral-900">Programme Selection</h2>
              <label className="block">
                <span className="text-sm font-medium text-neutral-700">Programme *</span>
                <select
                  required
                  value={formData.programme_applied || ''}
                  onChange={(e) => setFormData({ ...formData, programme_applied: e.target.value || null })}
                  className="mt-1 block w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option value="">Select a programme...</option>
                  {programmes?.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.level})
                    </option>
                  ))}
                </select>
              </label>
              <div className="flex justify-between pt-4">
                <Button type="button" variant="outline" onClick={() => setStep('personal')}>
                  Back
                </Button>
                <Button type="submit" loading={createApp.isPending}>
                  Next: Documents
                </Button>
              </div>
            </form>
          )}

          {step === 'documents' && (
            <div className="space-y-4">
              <h2 className="font-display text-lg font-bold text-neutral-900">Upload Documents</h2>
              <p className="text-sm text-neutral-600">
                Upload required documents. At minimum, upload your National ID and academic transcript.
              </p>
              <div className="space-y-3">
                {DOCUMENT_TYPES.map((docType) => {
                  const uploaded = uploadedDocs.filter((d) => d.type === docType.value)
                  return (
                    <div key={docType.value} className="rounded-lg border border-neutral-200 p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-neutral-900">{docType.label}</p>
                          {uploaded.length > 0 && (
                            <p className="mt-1 text-xs text-green-600">
                              {uploaded.map((d) => d.name).join(', ')}
                            </p>
                          )}
                        </div>
                        <label className="cursor-pointer">
                          <input
                            type="file"
                            className="hidden"
                            accept=".pdf,.jpg,.jpeg,.png"
                            onChange={(e) => {
                              const file = e.target.files?.[0]
                              if (file) handleFileUpload(docType.value, file)
                              e.target.value = ''
                            }}
                          />
                          <span className="inline-flex items-center gap-1 rounded-lg border border-neutral-300 px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50">
                            <DocumentArrowUpIcon className="h-4 w-4" />
                            Upload
                          </span>
                        </label>
                      </div>
                    </div>
                  )
                })}
              </div>
              <div className="flex justify-between pt-4">
                <Button type="button" variant="outline" onClick={() => setStep('programme')}>
                  Back
                </Button>
                <Button onClick={() => setStep('review')}>Next: Review</Button>
              </div>
            </div>
          )}

          {step === 'review' && (
            <div className="space-y-4">
              <h2 className="font-display text-lg font-bold text-neutral-900">Review & Submit</h2>
              <div className="rounded-lg border border-neutral-200 bg-neutral-50 p-4 space-y-2 text-sm">
                <div className="grid gap-2 sm:grid-cols-2">
                  <div><span className="font-medium text-neutral-500">Name:</span> {formData.full_name}</div>
                  <div><span className="font-medium text-neutral-500">Email:</span> {formData.email}</div>
                  <div><span className="font-medium text-neutral-500">National ID:</span> {formData.national_id}</div>
                  <div><span className="font-medium text-neutral-500">DOB:</span> {formData.date_of_birth}</div>
                  <div><span className="font-medium text-neutral-500">Gender:</span> {formData.gender}</div>
                  <div><span className="font-medium text-neutral-500">Phone:</span> {formData.phone_number}</div>
                </div>
                <div className="border-t border-neutral-200 pt-2">
                  <span className="font-medium text-neutral-500">Programme:</span>{' '}
                  {programmes?.find((p) => p.id === formData.programme_applied)?.name || 'Not selected'}
                </div>
                <div className="border-t border-neutral-200 pt-2">
                  <span className="font-medium text-neutral-500">Documents:</span>{' '}
                  {uploadedDocs.length > 0
                    ? uploadedDocs.map((d) => `${d.type} (${d.name})`).join(', ')
                    : 'None uploaded'}
                </div>
              </div>
              <div className="flex justify-between pt-4">
                <Button type="button" variant="outline" onClick={() => setStep('documents')}>
                  Back
                </Button>
                <Button onClick={handleSubmit} loading={submitApp.isPending}>
                  Submit Application
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
