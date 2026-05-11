from django.urls import path

from .views import (
    DocumentApproveView,
    DocumentArchiveView,
    DocumentDetailView,
    DocumentDownloadView,
    DocumentListCreateView,
    DocumentRejectView,
    DocumentSummaryView,
    MyDocumentListCreateView,
    StudentDocumentListCreateView,
)


urlpatterns = [
    path("documents", DocumentListCreateView.as_view(), name="documents-list-create"),
    path("documents/summary", DocumentSummaryView.as_view(), name="documents-summary"),
    path("documents/<uuid:document_id>", DocumentDetailView.as_view(), name="document-detail"),
    path("documents/<uuid:document_id>/download", DocumentDownloadView.as_view(), name="document-download"),
    path("documents/<uuid:document_id>/approve", DocumentApproveView.as_view(), name="document-approve"),
    path("documents/<uuid:document_id>/reject", DocumentRejectView.as_view(), name="document-reject"),
    path("documents/<uuid:document_id>/archive", DocumentArchiveView.as_view(), name="document-archive"),
    path("students/<uuid:student_id>/documents", StudentDocumentListCreateView.as_view(), name="student-documents-list-create"),
    path("me/documents", MyDocumentListCreateView.as_view(), name="me-documents-list-create"),
]
