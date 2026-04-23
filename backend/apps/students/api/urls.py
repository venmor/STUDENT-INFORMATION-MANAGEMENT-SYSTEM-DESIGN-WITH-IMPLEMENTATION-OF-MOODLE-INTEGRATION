from django.urls import path

from .views import (
    AdvisorAssignmentCreateView,
    AdvisingNoteDetailView,
    AdvisingNoteApproveView,
    AdvisingNoteListCreateView,
    FinancialFlagDetailView,
    FinancialFlagListCreateView,
    StudentDeactivateView,
    StudentCorrectionRequestDetailView,
    StudentCorrectionRequestListCreateView,
    StudentDetailView,
    StudentListCreateView,
)


urlpatterns = [
    path("students", StudentListCreateView.as_view(), name="students-list-create"),
    path("students/<uuid:student_id>", StudentDetailView.as_view(), name="student-detail"),
    path("students/<uuid:student_id>/deactivate", StudentDeactivateView.as_view(), name="student-deactivate"),
    path(
        "students/<uuid:student_id>/advisor-assignments",
        AdvisorAssignmentCreateView.as_view(),
        name="student-advisor-assignment-create",
    ),
    path(
        "students/<uuid:student_id>/financial-flags",
        FinancialFlagListCreateView.as_view(),
        name="student-financial-flags",
    ),
    path(
        "students/<uuid:student_id>/financial-flags/<uuid:flag_id>",
        FinancialFlagDetailView.as_view(),
        name="student-financial-flag-detail",
    ),
    path(
        "students/<uuid:student_id>/advising-notes",
        AdvisingNoteListCreateView.as_view(),
        name="student-advising-notes",
    ),
    path(
        "students/<uuid:student_id>/advising-notes/<uuid:note_id>",
        AdvisingNoteDetailView.as_view(),
        name="student-advising-note-detail",
    ),
    path(
        "students/<uuid:student_id>/advising-notes/<uuid:note_id>/approve",
        AdvisingNoteApproveView.as_view(),
        name="student-advising-note-approve",
    ),
    path(
        "students/<uuid:student_id>/correction-requests",
        StudentCorrectionRequestListCreateView.as_view(),
        name="student-correction-requests",
    ),
    path(
        "students/<uuid:student_id>/correction-requests/<uuid:correction_request_id>",
        StudentCorrectionRequestDetailView.as_view(),
        name="student-correction-request-detail",
    ),
]
