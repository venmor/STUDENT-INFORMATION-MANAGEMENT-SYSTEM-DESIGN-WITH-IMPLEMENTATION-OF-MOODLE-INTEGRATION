import { useMemo, useState } from 'react'
import { ArrowUpTrayIcon } from '@heroicons/react/24/outline'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import {
  documentTypeOptions,
  documentVisibilityOptions,
} from '@/features/documents/utils/documentLabels'
import type { DocumentType, DocumentVisibility, UploadDocumentPayload } from '@/types/documents'
import type { StudentProfile } from '@/types'

const allowedExtensions = '.pdf,.jpg,.jpeg,.png,.doc,.docx'
const maxUploadSize = 10 * 1024 * 1024

type FormErrors = Partial<Record<'studentId' | 'title' | 'file', string>>

export function DocumentUploadDialog({
  isPending = false,
  mode = 'admin',
  onOpenChange,
  onSubmit,
  open,
  students = [],
}: {
  isPending?: boolean
  mode?: 'admin' | 'student'
  onOpenChange: (open: boolean) => void
  onSubmit: (payload: UploadDocumentPayload) => void
  open: boolean
  students?: StudentProfile[]
}) {
  const [studentId, setStudentId] = useState('')
  const [documentType, setDocumentType] = useState<DocumentType>('OTHER')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [visibility, setVisibility] = useState<DocumentVisibility>('ADMIN_ONLY')
  const [file, setFile] = useState<File | null>(null)
  const [errors, setErrors] = useState<FormErrors>({})

  const studentItems = useMemo(
    () =>
      students.map((student) => ({
        value: student.id,
        label: `${student.full_name || student.username} (${student.student_number})`,
      })),
    [students],
  )

  function reset() {
    setStudentId('')
    setDocumentType('OTHER')
    setTitle('')
    setDescription('')
    setVisibility(mode === 'student' ? 'STUDENT_VISIBLE' : 'ADMIN_ONLY')
    setFile(null)
    setErrors({})
  }

  function validate(): boolean {
    const nextErrors: FormErrors = {}
    if (mode === 'admin' && !studentId) {
      nextErrors.studentId = 'Select the student this document belongs to.'
    }
    if (!title.trim()) {
      nextErrors.title = 'Title is required.'
    }
    if (!file) {
      nextErrors.file = 'Choose a document file.'
    } else if (file.size === 0) {
      nextErrors.file = 'The selected file is empty.'
    } else if (file.size > maxUploadSize) {
      nextErrors.file = 'The selected file exceeds the 10 MB limit.'
    }
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  function submit() {
    if (!validate() || !file) {
      return
    }
    onSubmit({
      studentId: mode === 'admin' ? studentId : undefined,
      documentType,
      title: title.trim(),
      description: description.trim(),
      visibility: mode === 'student' ? 'STUDENT_VISIBLE' : visibility,
      file,
    })
  }

  return (
    <Modal
      open={open}
      onOpenChange={(nextOpen) => {
        onOpenChange(nextOpen)
        if (!nextOpen) {
          reset()
        }
      }}
      title={mode === 'student' ? 'Upload Supporting Document' : 'Upload Document'}
      description="Allowed file types: PDF, JPG, PNG, DOC, and DOCX. Maximum size: 10 MB."
    >
      <div className="space-y-4">
        {mode === 'admin' ? (
          <div className="space-y-1.5">
            <Select
              id="document-student"
              label="Student"
              value={studentId || undefined}
              placeholder="Select a student"
              onValueChange={setStudentId}
              items={studentItems}
            />
            {errors.studentId ? (
              <p role="alert" className="text-sm text-danger">
                {errors.studentId}
              </p>
            ) : null}
          </div>
        ) : null}
        <Select
          id="document-upload-type"
          label="Document type"
          value={documentType}
          onValueChange={(value) => setDocumentType(value as DocumentType)}
          items={documentTypeOptions}
        />
        <Input
          id="document-title"
          label="Title"
          value={title}
          error={errors.title}
          onChange={(event) => setTitle(event.target.value)}
        />
        <Textarea
          id="document-description"
          label="Description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          rows={3}
        />
        {mode === 'admin' ? (
          <Select
            id="document-upload-visibility"
            label="Visibility"
            value={visibility}
            onValueChange={(value) => setVisibility(value as DocumentVisibility)}
            items={documentVisibilityOptions}
          />
        ) : null}
        <div className="space-y-1.5">
          <label htmlFor="document-file" className="block text-sm font-medium text-neutral-700">
            File
          </label>
          <input
            id="document-file"
            type="file"
            accept={allowedExtensions}
            aria-describedby="document-file-hint document-file-error"
            className="block w-full rounded-lg border border-neutral-300 px-4 py-2.5 text-sm text-neutral-900 file:mr-4 file:rounded-md file:border-0 file:bg-primary file:px-3 file:py-2 file:text-sm file:font-semibold file:text-white focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <p id="document-file-hint" className="text-sm text-neutral-500">
            Accepted: PDF, JPG, PNG, DOC, DOCX. Maximum size: 10 MB.
          </p>
          {file ? (
            <p className="max-w-full truncate text-sm text-neutral-700" title={file.name}>
              Selected file: {file.name}
            </p>
          ) : null}
          {errors.file ? (
            <p id="document-file-error" role="alert" className="text-sm text-danger">
              {errors.file}
            </p>
          ) : null}
        </div>
        <div className="flex flex-wrap justify-end gap-3">
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button loading={isPending} onClick={submit}>
            <ArrowUpTrayIcon className="h-4 w-4" />
            Upload Document
          </Button>
        </div>
      </div>
    </Modal>
  )
}
