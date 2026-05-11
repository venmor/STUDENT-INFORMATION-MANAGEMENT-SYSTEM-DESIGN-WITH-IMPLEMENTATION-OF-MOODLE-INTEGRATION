from django.urls import path

from .views import (
    AttendanceSessionCreateView,
    BulkEnrollmentCommitView,
    BulkEnrollmentPreviewView,
    CourseDetailView,
    CourseListCreateView,
    CoursePrerequisiteCreateView,
    EnrollmentCreateView,
    EnrollmentDropView,
    EnrollmentTransferView,
    GradeCreateView,
    GradeDetailView,
    GradeOfficialiseView,
    SectionCreateView,
    SectionDetailView,
    SectionRosterView,
    TranscriptView,
)


urlpatterns = [
    path("courses", CourseListCreateView.as_view(), name="courses-list-create"),
    path("courses/<uuid:course_id>", CourseDetailView.as_view(), name="course-detail"),
    path("courses/<uuid:course_id>/prerequisites", CoursePrerequisiteCreateView.as_view(), name="course-prerequisites-create"),
    path("sections", SectionCreateView.as_view(), name="sections-list-create"),
    path("sections/<uuid:section_id>", SectionDetailView.as_view(), name="section-detail"),
    path("sections/<uuid:section_id>/roster", SectionRosterView.as_view(), name="section-roster"),
    path("enrollments", EnrollmentCreateView.as_view(), name="enrollments-create"),
    path("enrollments/bulk-preview", BulkEnrollmentPreviewView.as_view(), name="enrollments-bulk-preview"),
    path("enrollments/bulk-commit", BulkEnrollmentCommitView.as_view(), name="enrollments-bulk-commit"),
    path("enrollments/<uuid:enrollment_id>/drop", EnrollmentDropView.as_view(), name="enrollment-drop"),
    path("enrollments/<uuid:enrollment_id>/transfer", EnrollmentTransferView.as_view(), name="enrollment-transfer"),
    path("attendance/sessions", AttendanceSessionCreateView.as_view(), name="attendance-session-create"),
    path("grades", GradeCreateView.as_view(), name="grades-create"),
    path("grades/<uuid:grade_id>", GradeDetailView.as_view(), name="grade-detail"),
    path("grades/<uuid:grade_id>/officialise", GradeOfficialiseView.as_view(), name="grade-officialise"),
    path("students/<uuid:student_id>/transcript", TranscriptView.as_view(), name="student-transcript"),
]
