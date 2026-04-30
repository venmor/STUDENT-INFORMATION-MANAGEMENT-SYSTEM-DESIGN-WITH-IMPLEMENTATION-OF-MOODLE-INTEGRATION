from __future__ import annotations

import csv
from io import StringIO

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditCategory, AuditSeverity
from apps.audit.services import record_audit_event_safely
from apps.reporting.services import (
    ReportFilters,
    get_admin_reporting_summary,
    get_calendar_deadline_report,
    get_capacity_report,
    get_enrollment_report,
    get_grade_report,
    get_moodle_sync_report,
    get_operational_activity_report,
)


def filters_from_request(request) -> ReportFilters:
    return ReportFilters.from_params(request.query_params)


class AdminReportSummaryView(APIView):
    def get(self, request):
        filters = filters_from_request(request)
        record_audit_event_safely(
            actor=request.user,
            category=AuditCategory.SYSTEM,
            action="ADMIN_REPORT_VIEWED",
            summary="Admin viewed the institutional reporting dashboard.",
            target_type="AdminReport",
            target_id="summary",
            severity=AuditSeverity.INFO,
            metadata={
                "reportType": "summary",
                "filters": filters.as_metadata(),
            },
            request=request,
        )
        return Response(get_admin_reporting_summary(filters), status=status.HTTP_200_OK)


class AdminReportEnrollmentView(APIView):
    def get(self, request):
        return Response(get_enrollment_report(filters_from_request(request)), status=status.HTTP_200_OK)


class AdminReportCapacityView(APIView):
    def get(self, request):
        return Response(get_capacity_report(filters_from_request(request)), status=status.HTTP_200_OK)


class AdminReportCapacityExportView(APIView):
    def get(self, request):
        report = get_capacity_report(filters_from_request(request))
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "Course Code",
                "Course Title",
                "Section",
                "Academic Year",
                "Semester",
                "Faculty",
                "Capacity",
                "Enrolled",
                "Remaining Seats",
                "Fill Rate",
                "Status",
            ]
        )
        for section in report["sections"]:
            writer.writerow(
                [
                    section["courseCode"],
                    section["courseTitle"],
                    section["sectionCode"],
                    section["academicYear"],
                    section["semester"],
                    section["facultyName"],
                    section["capacity"],
                    section["enrolledCount"],
                    section["remainingSeats"],
                    section["fillRate"],
                    section["status"],
                ]
            )

        record_audit_event_safely(
            actor=request.user,
            category=AuditCategory.SYSTEM,
            action="ADMIN_REPORT_EXPORTED",
            summary="Admin exported the section capacity report.",
            target_type="AdminReport",
            target_id="capacity",
            severity=AuditSeverity.INFO,
            metadata={
                "reportType": "capacity",
                "rowCount": len(report["sections"]),
                "filters": filters_from_request(request).as_metadata(),
            },
            request=request,
        )

        response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="section-capacity-report.csv"'
        return response


class AdminReportGradesView(APIView):
    def get(self, request):
        return Response(get_grade_report(filters_from_request(request)), status=status.HTTP_200_OK)


class AdminReportMoodleSyncView(APIView):
    def get(self, request):
        return Response(get_moodle_sync_report(filters_from_request(request)), status=status.HTTP_200_OK)


class AdminReportCalendarView(APIView):
    def get(self, request):
        return Response(get_calendar_deadline_report(filters_from_request(request)), status=status.HTTP_200_OK)


class AdminReportActivityView(APIView):
    def get(self, request):
        return Response(get_operational_activity_report(filters_from_request(request)), status=status.HTTP_200_OK)
