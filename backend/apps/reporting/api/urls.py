from django.urls import path

from .views import (
    AdminReportActivityView,
    AdminReportCalendarView,
    AdminReportCapacityExportView,
    AdminReportCapacityView,
    AdminReportEnrollmentView,
    AdminReportGradesView,
    AdminReportMoodleSyncView,
    AdminReportDocumentsView,
    AdminReportSummaryView,
)


urlpatterns = [
    path("admin/reports/summary/", AdminReportSummaryView.as_view(), name="admin-report-summary"),
    path("admin/reports/enrollment/", AdminReportEnrollmentView.as_view(), name="admin-report-enrollment"),
    path("admin/reports/capacity/", AdminReportCapacityView.as_view(), name="admin-report-capacity"),
    path(
        "admin/reports/capacity/export.csv",
        AdminReportCapacityExportView.as_view(),
        name="admin-report-capacity-export",
    ),
    path("admin/reports/grades/", AdminReportGradesView.as_view(), name="admin-report-grades"),
    path("admin/reports/moodle-sync/", AdminReportMoodleSyncView.as_view(), name="admin-report-moodle-sync"),
    path("admin/reports/calendar/", AdminReportCalendarView.as_view(), name="admin-report-calendar"),
    path("admin/reports/activity/", AdminReportActivityView.as_view(), name="admin-report-activity"),
    path("admin/reports/documents/", AdminReportDocumentsView.as_view(), name="admin-report-documents"),
]
