from django.urls import path

from apps.admissions.views import (
    AdminApplicationApproveView,
    AdminApplicationDetailView,
    AdminApplicationListView,
    AdminApplicationRejectView,
    PublicApplicationCreateView,
    PublicApplicationSubmitView,
    PublicDocumentUploadView,
)

urlpatterns = [
    path("admissions/apply", PublicApplicationCreateView.as_view(), name="admissions-apply"),
    path("admissions/apply/<uuid:applicant_id>/documents", PublicDocumentUploadView.as_view(), name="admissions-upload-doc"),
    path("admissions/apply/<uuid:applicant_id>/submit", PublicApplicationSubmitView.as_view(), name="admissions-submit"),
    path("admissions/applications", AdminApplicationListView.as_view(), name="admissions-list"),
    path("admissions/applications/<uuid:applicant_id>", AdminApplicationDetailView.as_view(), name="admissions-detail"),
    path("admissions/applications/<uuid:applicant_id>/approve", AdminApplicationApproveView.as_view(), name="admissions-approve"),
    path("admissions/applications/<uuid:applicant_id>/reject", AdminApplicationRejectView.as_view(), name="admissions-reject"),
]
