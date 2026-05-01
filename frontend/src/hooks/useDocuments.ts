import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  approveDocument,
  archiveDocument,
  downloadDocument,
  getDocumentReport,
  getDocumentSummary,
  getDocuments,
  getMyDocuments,
  getStudentDocuments,
  rejectDocument,
  uploadDocument,
  uploadMyDocument,
} from '@/api/documents'
import { filenameFromContentDisposition } from '@/features/documents/utils/documentFormatting'
import type { DocumentFilters, UploadDocumentPayload } from '@/types/documents'

export function useDocuments(filters: DocumentFilters = {}) {
  return useQuery({
    queryKey: ['documents', filters],
    queryFn: () => getDocuments(filters),
  })
}

export function useStudentDocuments(studentId?: string, filters: DocumentFilters = {}) {
  return useQuery({
    queryKey: ['documents', 'student', studentId, filters],
    queryFn: () => getStudentDocuments(studentId!, filters),
    enabled: Boolean(studentId),
  })
}

export function useMyDocuments(filters: DocumentFilters = {}) {
  return useQuery({
    queryKey: ['documents', 'me', filters],
    queryFn: () => getMyDocuments(filters),
  })
}

export function useDocumentSummary() {
  return useQuery({
    queryKey: ['documents', 'summary'],
    queryFn: getDocumentSummary,
  })
}

export function useDocumentReport() {
  return useQuery({
    queryKey: ['admin-reports', 'documents'],
    queryFn: getDocumentReport,
  })
}

export function useUploadDocument(scope: 'admin' | 'student' = 'admin') {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: UploadDocumentPayload) => (scope === 'student' ? uploadMyDocument(payload) : uploadDocument(payload)),
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: ['documents'] }),
        queryClient.invalidateQueries({ queryKey: ['admin-reports'] }),
      ]),
  })
}

export function useApproveDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: approveDocument,
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: ['documents'] }),
        queryClient.invalidateQueries({ queryKey: ['admin-reports'] }),
      ]),
  })
}

export function useRejectDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: rejectDocument,
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: ['documents'] }),
        queryClient.invalidateQueries({ queryKey: ['admin-reports'] }),
      ]),
  })
}

export function useArchiveDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: archiveDocument,
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: ['documents'] }),
        queryClient.invalidateQueries({ queryKey: ['admin-reports'] }),
      ]),
  })
}

export function useDownloadDocument() {
  return useMutation({
    mutationFn: async ({ documentId, fallbackFilename }: { documentId: string; fallbackFilename: string }) => {
      const result = await downloadDocument(documentId)
      const url = window.URL.createObjectURL(result.blob)
      const link = window.document.createElement('a')
      link.href = url
      link.download = filenameFromContentDisposition(result.contentDisposition) || fallbackFilename
      window.document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    },
  })
}
