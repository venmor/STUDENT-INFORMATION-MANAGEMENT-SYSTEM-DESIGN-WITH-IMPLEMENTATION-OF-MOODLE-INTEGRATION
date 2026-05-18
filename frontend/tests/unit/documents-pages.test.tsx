import { fireEvent, render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { AdminDocumentsPage } from '@/pages/admin/Documents'
import { StudentDocumentsPage } from '@/pages/student/Documents'
import { useAuthStore } from '@/stores/authStore'
import type { StudentDocument } from '@/types/documents'
import type { PrimaryRole, StudentProfile } from '@/types'

const mocks = vi.hoisted(() => ({
  archiveMutate: vi.fn(),
  approveMutate: vi.fn(),
  downloadMutate: vi.fn(),
  rejectMutate: vi.fn(),
  uploadMutate: vi.fn(),
  refetchDocuments: vi.fn(),
  refetchSummary: vi.fn(),
  state: {} as Record<string, unknown>,
}))

vi.mock('@/hooks/useDocuments', () => ({
  useArchiveDocument: () => ({ mutate: mocks.archiveMutate, isPending: false }),
  useApproveDocument: () => ({ mutate: mocks.approveMutate, isPending: false }),
  useDocumentSummary: () => mocks.state.summary,
  useDocuments: () => mocks.state.documents,
  useDownloadDocument: () => ({ mutate: mocks.downloadMutate, isPending: false }),
  useMyDocuments: () => mocks.state.myDocuments,
  useRejectDocument: () => ({ mutate: mocks.rejectMutate, isPending: false }),
  useUploadDocument: () => ({ mutate: mocks.uploadMutate, isPending: false }),
}))

vi.mock('@/hooks/useStudents', () => ({
  useStudents: () => mocks.state.students,
}))

function queryResult(data: unknown, overrides: Record<string, unknown> = {}) {
  return {
    data,
    isLoading: false,
    isError: false,
    refetch: overrides.refetch ?? vi.fn(),
    ...overrides,
  }
}

const student: StudentProfile = {
  id: 'student-1',
  user_id: 101,
  username: 'student.demo1',
  full_name: 'Catherine Banda',
  email: 'student.demo1@example.edu',
  student_number: 'SIS-0001',
  national_id: '111111/11/1',
  date_of_birth: '2003-01-15',
  gender: 'Female',
  programme: 'Computer Science',
  year_of_study: 4,
  academic_standing: 'GOOD',
  cumulative_gpa: '3.40',
  standing_override_reason: '',
  is_active: true,
  attendance_flags: [],
  attendance_percentages: [],
}

const documents: StudentDocument[] = [
  {
    id: 'document-1',
    student: {
      id: student.id,
      studentNumber: student.student_number,
      fullName: student.full_name,
      programme: student.programme,
    },
    documentType: 'TRANSCRIPT',
    title: 'Semester 1 Transcript',
    description: 'Uploaded transcript copy.',
    originalFilename: 'transcript.pdf',
    contentType: 'application/pdf',
    fileSize: 204800,
    visibility: 'STUDENT_VISIBLE',
    status: 'PENDING_REVIEW',
    uploadedBy: { id: 1, username: 'admin.demo', fullName: 'Admin Demo' },
    reviewedBy: null,
    reviewedAt: null,
    reviewNote: '',
    metadata: { source: 'demo' },
    createdAt: '2026-05-01T10:00:00Z',
    updatedAt: '2026-05-01T10:00:00Z',
    canDownload: true,
    canReview: true,
    canArchive: true,
  },
  {
    id: 'document-2',
    student: {
      id: student.id,
      studentNumber: student.student_number,
      fullName: student.full_name,
      programme: student.programme,
    },
    documentType: 'APPEAL_LETTER',
    title: 'Appeal Letter',
    description: '',
    originalFilename: 'appeal.pdf',
    contentType: 'application/pdf',
    fileSize: 1024,
    visibility: 'STUDENT_VISIBLE',
    status: 'REJECTED',
    uploadedBy: { id: 101, username: 'student.demo1', fullName: 'Catherine Banda' },
    reviewedBy: { id: 1, username: 'admin.demo', fullName: 'Admin Demo' },
    reviewedAt: '2026-05-01T11:00:00Z',
    reviewNote: 'Please upload the signed copy.',
    metadata: {},
    createdAt: '2026-05-01T09:00:00Z',
    updatedAt: '2026-05-01T11:00:00Z',
    canDownload: true,
    canReview: false,
    canArchive: false,
  },
]

const summary = {
  total: 2,
  pendingReview: 1,
  approved: 0,
  rejected: 1,
  archived: 0,
  studentVisible: 2,
  adminOnly: 0,
  recentUploads: 2,
  byType: {
    NRC_ID: 0,
    OFFICIAL_LETTER: 0,
    TRANSCRIPT: 1,
    APPEAL_LETTER: 1,
    CLEARANCE_FORM: 0,
    MEDICAL_SUPPORT: 0,
    OTHER: 0,
  },
}

function setSession(primaryRole: PrimaryRole) {
  useAuthStore.getState().setSession({
    accessToken: 'access-token',
    refreshToken: 'refresh-token',
    expiresAt: Date.now() + 1000 * 60 * 15,
    user: {
      id: primaryRole === 'STUDENT' ? 101 : 1,
      username: `${primaryRole.toLowerCase()}.one`,
      fullName: `${primaryRole} One`,
      primaryRole,
      mustResetPassword: false,
      studentProfileId: primaryRole === 'STUDENT' ? student.id : null,
    },
  })
}

function setDefaultHookState(overrides: Record<string, unknown> = {}) {
  mocks.state = {
    documents: queryResult(documents, { refetch: mocks.refetchDocuments }),
    myDocuments: queryResult(documents.slice(1), { refetch: mocks.refetchDocuments }),
    students: queryResult([student]),
    summary: queryResult(summary, { refetch: mocks.refetchSummary }),
    ...overrides,
  }
}

function renderAdminPage() {
  setSession('ADMIN')
  return render(
    <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
      <AdminDocumentsPage />
    </MemoryRouter>,
  )
}

function renderStudentPage() {
  setSession('STUDENT')
  return render(
    <MemoryRouter future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
      <StudentDocumentsPage />
    </MemoryRouter>,
  )
}

describe('document management pages', () => {
  beforeEach(() => {
    sessionStorage.clear()
    useAuthStore.getState().logout()
    mocks.archiveMutate.mockClear()
    mocks.approveMutate.mockClear()
    mocks.downloadMutate.mockClear()
    mocks.rejectMutate.mockClear()
    mocks.uploadMutate.mockClear()
    mocks.refetchDocuments.mockClear()
    mocks.refetchSummary.mockClear()
    setDefaultHookState()
  })

  it('renders the admin workflow with summary cards, filters, table actions, details, upload validation, and no emoji text', () => {
    const { container } = renderAdminPage()

    expect(screen.getByText('Total Documents')).toBeInTheDocument()
    expect(screen.getAllByText('Pending Review').length).toBeGreaterThan(0)
    expect(screen.getByText('Workflow Health')).toBeInTheDocument()
    expect(screen.getByText('Review Queue')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Document Repository' })).toBeInTheDocument()
    expect(screen.getByLabelText('Search')).toBeInTheDocument()
    expect(screen.getByLabelText('Document type')).toBeInTheDocument()
    expect(screen.getByLabelText('Status')).toBeInTheDocument()
    expect(screen.getByLabelText('Visibility')).toBeInTheDocument()
    expect(screen.getAllByText('Catherine Banda').length).toBeGreaterThan(0)
    expect(screen.getByText('Semester 1 Transcript')).toBeInTheDocument()
    expect(screen.getAllByText('Student Visible').length).toBeGreaterThan(0)
    expect(screen.getByRole('button', { name: /Approve/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Reject/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Archive/i })).toBeInTheDocument()
    expect(screen.getByText('Document privacy')).toBeInTheDocument()

    fireEvent.click(screen.getAllByRole('button', { name: 'View Details' })[0])
    expect(screen.getByRole('heading', { name: 'Document Details' })).toBeInTheDocument()
    expect(screen.getByText('Audit-Safe Metadata')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Upload Document' }))
    const dialog = within(screen.getByRole('dialog'))
    expect(dialog.getByLabelText('Student')).toBeInTheDocument()
    expect(dialog.getByLabelText('File')).toBeInTheDocument()
    expect(dialog.getByText('Accepted: PDF, JPG, PNG, DOC, DOCX. Maximum size: 10 MB.')).toBeInTheDocument()
    fireEvent.click(dialog.getByRole('button', { name: 'Upload Document' }))
    expect(dialog.getByText('Select the student this document belongs to.')).toBeInTheDocument()
    expect(dialog.getByText('Title is required.')).toBeInTheDocument()
    expect(dialog.getByText('Choose a document file.')).toBeInTheDocument()

    expect(container.textContent).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u)
  })

  it('runs admin review, archive, download, and refresh actions through mutations', () => {
    renderAdminPage()

    fireEvent.click(screen.getByRole('button', { name: /Approve/i }))
    let dialog = within(screen.getByRole('dialog'))
    fireEvent.change(dialog.getByLabelText('Review note'), { target: { value: 'Verified.' } })
    fireEvent.click(dialog.getByRole('button', { name: 'Approve document' }))
    expect(mocks.approveMutate).toHaveBeenCalledWith(
      { documentId: 'document-1', reviewNote: 'Verified.' },
      expect.any(Object),
    )
    fireEvent.click(dialog.getByRole('button', { name: 'Cancel' }))

    fireEvent.click(screen.getByRole('button', { name: /Reject/i }))
    dialog = within(screen.getByRole('dialog'))
    fireEvent.change(dialog.getByLabelText('Review note'), { target: { value: 'Replace file.' } })
    fireEvent.click(dialog.getByRole('button', { name: 'Reject document' }))
    expect(mocks.rejectMutate).toHaveBeenCalledWith(
      { documentId: 'document-1', reviewNote: 'Replace file.' },
      expect.any(Object),
    )
    fireEvent.click(dialog.getByRole('button', { name: 'Cancel' }))

    fireEvent.click(screen.getByRole('button', { name: /Archive/i }))
    expect(mocks.archiveMutate).toHaveBeenCalledWith('document-1')

    fireEvent.click(screen.getAllByRole('button', { name: /Download/i })[0])
    expect(mocks.downloadMutate).toHaveBeenCalledWith({ documentId: 'document-1', fallbackFilename: 'transcript.pdf' })

    fireEvent.click(screen.getByRole('button', { name: 'Refresh' }))
    expect(mocks.refetchDocuments).toHaveBeenCalled()
    expect(mocks.refetchSummary).toHaveBeenCalled()
  })

  it('renders the student document workflow without admin-only actions', () => {
    const { container } = renderStudentPage()

    expect(screen.getByText('Shared Documents')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'My Documents' })).toBeInTheDocument()
    expect(screen.getByText('Documents shared with you by the institution and supporting files you have uploaded.')).toBeInTheDocument()
    expect(screen.getAllByText('Appeal Letter').length).toBeGreaterThan(0)
    fireEvent.click(screen.getAllByRole('button', { name: 'View Details' })[0])
    expect(screen.getByText('Please upload the signed copy.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Upload Supporting Document' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Approve/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Archive/i })).not.toBeInTheDocument()
    expect(screen.getByText('Students may upload supporting files for review.')).toBeInTheDocument()
    expect(container.textContent).not.toMatch(/[\u{1F300}-\u{1FAFF}]/u)
  })

  it('renders empty and error states', () => {
    setDefaultHookState({
      documents: queryResult([], { refetch: mocks.refetchDocuments }),
      myDocuments: queryResult([], { refetch: mocks.refetchDocuments }),
    })
    const { unmount } = renderAdminPage()

    expect(screen.getByText('No student documents found')).toBeInTheDocument()
    expect(screen.getByText('Upload a document or seed demo document records to test the workflow.')).toBeInTheDocument()
    unmount()

    setDefaultHookState({
      documents: queryResult(undefined, { isError: true, refetch: mocks.refetchDocuments }),
      myDocuments: queryResult(undefined, { isError: true, refetch: mocks.refetchDocuments }),
    })
    renderAdminPage()

    expect(screen.getByText('Could not load student documents')).toBeInTheDocument()
    expect(screen.getByText('Check the backend API and your admin session.')).toBeInTheDocument()
  })
})
