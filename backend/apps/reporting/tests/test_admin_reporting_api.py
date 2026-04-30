from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.academics.models import (
    Course,
    CourseSection,
    CourseSectionStatus,
    Enrollment,
    EnrollmentEvent,
    EnrollmentEventType,
    EnrollmentStatus,
    GradeRecord,
    GradeStatus,
)
from apps.accounts.constants import RoleCode
from apps.audit.models import AuditCategory, AuditEvent, AuditSeverity
from apps.audit.services import record_audit_event
from apps.calendar.models import (
    AcademicCalendarAudience,
    AcademicCalendarEvent,
    AcademicCalendarEventType,
    AcademicCalendarPriority,
    AcademicCalendarSource,
    AcademicCalendarStatus,
)
from apps.integration.models import (
    IntegrationEventStatus,
    IntegrationOutboxEvent,
    MoodleCourseMap,
    MoodleEngagementIngestionRun,
    MoodleEngagementIngestionStatus,
    MoodleEngagementSnapshot,
    MoodleUserMap,
)
from apps.notifications.models import NotificationCategory, NotificationSeverity
from apps.notifications.services import create_notification
from apps.students.models import AcademicStanding, FinancialFlag, StudentProfile
from apps.testutils import authenticated_client_for_user, create_user


def create_role_user(role: str, username: str):
    return create_user(
        username=username,
        email=f"{username}@example.com",
        password="Secret123!",
        primary_role=role,
        full_name=username.replace("-", " ").title(),
    )


def create_student(
    *,
    username: str,
    programme: str = "BSc Computer Science",
    active: bool = True,
    standing: str = AcademicStanding.GOOD_STANDING,
) -> StudentProfile:
    user = create_role_user(RoleCode.STUDENT, username)
    return StudentProfile.objects.create(
        user=user,
        student_number=f"2026-CS-{username[-1]}",
        national_id=f"NRC-{username}",
        date_of_birth=timezone.localdate() - timedelta(days=365 * 20),
        gender="Female",
        programme=programme,
        year_of_study=3,
        academic_standing=standing,
        is_active=active,
    )


def create_section(
    *,
    faculty,
    course_code: str,
    section_code: str,
    capacity: int,
    academic_year: str = "2026/2027",
    semester: str = "Semester 1",
) -> CourseSection:
    course = Course.objects.create(
        course_code=course_code,
        course_title=f"{course_code} Title",
        department="Computer Science",
        credit_hours=3,
        programme_code="BSc Computer Science",
        max_capacity=capacity,
        is_active=True,
    )
    now = timezone.now()
    return CourseSection.objects.create(
        course=course,
        section_code=section_code,
        faculty_user=faculty,
        room="LT-1",
        semester=semester,
        academic_year=academic_year,
        max_capacity=capacity,
        registration_opens_at=now - timedelta(days=14),
        registration_closes_at=now + timedelta(days=14),
        drop_deadline=now + timedelta(days=21),
        attendance_threshold=Decimal("75.00"),
        status=CourseSectionStatus.ACTIVE,
    )


def create_enrollment(student, section, status=EnrollmentStatus.ENROLLED, *, active=True, actor=None):
    enrollment = Enrollment.objects.create(
        student=student,
        section=section,
        enrollment_status=status,
        actor_role=RoleCode.ADMIN,
        actor_user=actor,
        is_active=active,
    )
    EnrollmentEvent.objects.create(
        enrollment=enrollment,
        event_type=EnrollmentEventType.ENROLL if status != EnrollmentStatus.DROPPED else EnrollmentEventType.DROP,
        actor_role=RoleCode.ADMIN,
        actor_user=actor,
        details={"reportingTest": True},
    )
    return enrollment


def reporting_paths() -> list[str]:
    return [
        "/api/v1/admin/reports/summary/",
        "/api/v1/admin/reports/enrollment/",
        "/api/v1/admin/reports/capacity/",
        "/api/v1/admin/reports/grades/",
        "/api/v1/admin/reports/moodle-sync/",
        "/api/v1/admin/reports/calendar/",
        "/api/v1/admin/reports/activity/",
        "/api/v1/admin/reports/capacity/export.csv",
    ]


def seed_reporting_data(settings):
    settings.MOODLE_WS_TOKEN = "super-secret-token"
    admin = create_role_user(RoleCode.ADMIN, "report-admin")
    faculty = create_role_user(RoleCode.FACULTY, "report-faculty")
    students = [
        create_student(username="report-student-1"),
        create_student(username="report-student-2", standing=AcademicStanding.ACADEMIC_WARNING),
        create_student(username="report-student-3"),
        create_student(username="report-student-4"),
        create_student(username="report-student-5", programme="BSc Information Systems", active=False),
    ]
    section_full = create_section(faculty=faculty, course_code="CSC351", section_code="A1", capacity=2)
    section_near = create_section(faculty=faculty, course_code="CSC352", section_code="A1", capacity=5)
    section_over = create_section(faculty=faculty, course_code="CSC353", section_code="A1", capacity=1)
    section_open = create_section(faculty=faculty, course_code="CSC354", section_code="A1", capacity=10)

    for student in students[:2]:
        create_enrollment(student, section_full, actor=admin)
    for student in students[:4]:
        create_enrollment(student, section_near, actor=admin)
    for student in students[:2]:
        create_enrollment(student, section_over, actor=admin)
    create_enrollment(students[2], section_open, actor=admin)
    create_enrollment(students[3], section_open, EnrollmentStatus.WAITLISTED, active=False, actor=admin)
    create_enrollment(students[3], section_full, EnrollmentStatus.DROPPED, active=False, actor=admin)

    GradeRecord.objects.create(
        student=students[0],
        section=section_full,
        numeric_score=Decimal("85.00"),
        letter_grade="A",
        grade_points=Decimal("4.00"),
        grade_status=GradeStatus.OFFICIAL,
        entered_by_user=faculty,
        officialised_by_user=admin,
        officialised_at=timezone.now(),
    )
    GradeRecord.objects.create(
        student=students[1],
        section=section_full,
        numeric_score=Decimal("73.00"),
        letter_grade="B",
        grade_points=Decimal("3.00"),
        grade_status=GradeStatus.DRAFT,
        entered_by_user=faculty,
    )
    for student in students[:2]:
        GradeRecord.objects.create(
            student=student,
            section=section_near,
            numeric_score=Decimal("79.00"),
            letter_grade="B+",
            grade_points=Decimal("3.50"),
            grade_status=GradeStatus.OFFICIAL,
            entered_by_user=faculty,
            officialised_by_user=admin,
            officialised_at=timezone.now(),
        )
    GradeRecord.objects.create(
        student=students[2],
        section=section_open,
        numeric_score=Decimal("68.00"),
        letter_grade="C+",
        grade_points=Decimal("2.50"),
        grade_status=GradeStatus.OFFICIAL,
        entered_by_user=faculty,
        officialised_by_user=admin,
        officialised_at=timezone.now(),
    )

    FinancialFlag.objects.create(
        student=students[1],
        flag_type="REGISTRATION_HOLD",
        reason="Demo active hold",
        effective_date=timezone.localdate(),
        created_by_user=admin,
    )

    pending = IntegrationOutboxEvent.objects.create(event_type="USER_SYNC_REQUESTED", payload={"user_id": admin.id})
    processed = IntegrationOutboxEvent.objects.create(
        event_type="COURSE_SYNC_REQUESTED",
        payload={"section_id": str(section_full.id)},
        status=IntegrationEventStatus.PROCESSED,
        processed_at=timezone.now(),
    )
    failed = IntegrationOutboxEvent.objects.create(
        event_type="GRADE_SYNC_REQUESTED",
        payload={"grade_id": "grade-1", "wstoken": "super-secret-token"},
        status=IntegrationEventStatus.FAILED,
        attempts=2,
        last_error="Moodle rejected token super-secret-token",
        last_attempt_at=timezone.now(),
    )
    MoodleUserMap.objects.create(user=students[0].user, moodle_user_id=5001, moodle_username=students[0].user.username)
    MoodleCourseMap.objects.create(section=section_full, moodle_course_id=8801, moodle_shortname="CSC351-A1", moodle_category_id=7)
    run = MoodleEngagementIngestionRun.objects.create(
        status=MoodleEngagementIngestionStatus.PARTIAL,
        completed_at=timezone.now(),
        courses_inspected=1,
        users_inspected=2,
        snapshots_created=1,
        failure_count=1,
        last_error="safe partial failure",
    )
    MoodleEngagementSnapshot.objects.create(
        run=run,
        user=students[0].user,
        student=students[0],
        section=section_full,
        moodle_user_id=5001,
        moodle_course_id=8801,
        moodle_course_last_access_at=timezone.now() - timedelta(days=1),
        collected_at=timezone.now(),
    )

    now = timezone.now()
    AcademicCalendarEvent.objects.create(
        title="Registration deadline",
        description="Last day to register.",
        event_type=AcademicCalendarEventType.REGISTRATION_DEADLINE,
        audience=AcademicCalendarAudience.STUDENTS,
        priority=AcademicCalendarPriority.CRITICAL,
        academic_year="2026/2027",
        semester="Semester 1",
        start_at=now + timedelta(days=1),
        source=AcademicCalendarSource.MANUAL,
        status=AcademicCalendarStatus.ACTIVE,
        created_by=admin,
    )
    AcademicCalendarEvent.objects.create(
        title="Grade submission deadline",
        description="Faculty grade deadline.",
        event_type=AcademicCalendarEventType.GRADE_SUBMISSION_DEADLINE,
        audience=AcademicCalendarAudience.FACULTY,
        priority=AcademicCalendarPriority.HIGH,
        academic_year="2026/2027",
        semester="Semester 1",
        start_at=now + timedelta(days=2),
        source=AcademicCalendarSource.MANUAL,
        status=AcademicCalendarStatus.ACTIVE,
        created_by=admin,
    )
    AcademicCalendarEvent.objects.create(
        title="Exam period",
        description="Final exams.",
        event_type=AcademicCalendarEventType.EXAM_PERIOD,
        audience=AcademicCalendarAudience.ALL,
        priority=AcademicCalendarPriority.NORMAL,
        academic_year="2026/2027",
        semester="Semester 1",
        start_at=now + timedelta(days=10),
        source=AcademicCalendarSource.MANUAL,
        status=AcademicCalendarStatus.ACTIVE,
        created_by=admin,
    )

    create_notification(
        recipient=admin,
        category=NotificationCategory.SYSTEM,
        severity=NotificationSeverity.WARNING,
        title="Report demo notification",
        message="Unread admin notification.",
        action_url="/admin/reports",
    )
    create_notification(
        recipient=admin,
        category=NotificationCategory.MOODLE,
        severity=NotificationSeverity.ERROR,
        title="Read notification",
        message="Already read.",
        is_read=True,
    )
    record_audit_event(
        actor=admin,
        category=AuditCategory.SYSTEM,
        action="SYSTEM_WARNING",
        summary="Warning event.",
        severity=AuditSeverity.WARNING,
    )
    record_audit_event(
        actor=admin,
        category=AuditCategory.MOODLE,
        action="MOODLE_SYNC_FAILED",
        summary="Moodle failure.",
        severity=AuditSeverity.ERROR,
    )

    return {
        "admin": admin,
        "faculty": faculty,
        "students": students,
        "section_full": section_full,
        "section_near": section_near,
        "section_over": section_over,
        "section_open": section_open,
        "pending": pending,
        "processed": processed,
        "failed": failed,
        "run": run,
    }


@pytest.mark.django_db
def test_admin_can_access_each_reporting_endpoint(settings):
    records = seed_reporting_data(settings)
    client = authenticated_client_for_user(records["admin"])

    for path in reporting_paths():
        response = client.get(path)
        assert response.status_code == 200, path


@pytest.mark.django_db
def test_unauthenticated_users_receive_401(settings):
    seed_reporting_data(settings)

    for path in reporting_paths():
        response = APIClient().get(path)
        assert response.status_code == 401, path


@pytest.mark.parametrize("role", [RoleCode.STUDENT, RoleCode.ADVISOR, RoleCode.FACULTY])
@pytest.mark.django_db
def test_non_admin_users_receive_403(settings, role):
    seed_reporting_data(settings)
    user = create_role_user(role, f"report-denied-{role.lower()}")
    client = authenticated_client_for_user(user)

    for path in reporting_paths():
        response = client.get(path)
        assert response.status_code == 403, path


@pytest.mark.django_db
def test_summary_counts_match_seeded_data(settings):
    records = seed_reporting_data(settings)
    response = authenticated_client_for_user(records["admin"]).get("/api/v1/admin/reports/summary/")

    assert response.status_code == 200
    data = response.json()
    assert data["students"]["total"] == 5
    assert data["students"]["active"] == 4
    assert data["students"]["inactive"] == 1
    assert data["students"]["byProgramme"][0]["programme"] == "BSc Computer Science"
    assert data["students"]["byProgramme"][0]["total"] == 4
    assert data["enrollments"] == {
        "total": 11,
        "currentTerm": 11,
        "pending": 1,
        "confirmed": 9,
        "dropped": 1,
    }
    assert data["capacity"]["sectionsTotal"] == 4
    assert data["capacity"]["sectionsNearCapacity"] == 1
    assert data["capacity"]["sectionsFull"] == 2
    assert data["capacity"]["averageFillRate"] == 97.5
    assert data["grades"]["draft"] == 1
    assert data["grades"]["official"] == 4
    assert data["grades"]["pendingApproval"] == 0
    assert data["grades"]["completionRate"] == 44.44
    assert data["moodle"]["pendingEvents"] == 1
    assert data["moodle"]["failedEvents"] == 1
    assert data["moodle"]["processedEvents"] == 1
    assert data["moodle"]["userMappings"] == 1
    assert data["moodle"]["courseMappings"] == 1
    assert data["moodle"]["latestEngagementRunStatus"] == "PARTIAL"
    assert data["calendar"]["upcomingDeadlines"] == 3
    assert data["calendar"]["criticalDeadlines"] == 1
    assert data["calendar"]["nextDeadlineTitle"] == "Registration deadline"
    assert data["activity"]["auditEventsToday"] >= 2
    assert data["activity"]["unreadAdminNotifications"] == 1
    assert AuditEvent.objects.filter(
        actor=records["admin"],
        category=AuditCategory.SYSTEM,
        action="ADMIN_REPORT_VIEWED",
        target_type="AdminReport",
        target_id="summary",
        severity=AuditSeverity.INFO,
    ).exists()


@pytest.mark.django_db
def test_capacity_report_computes_remaining_fill_and_status(settings):
    records = seed_reporting_data(settings)
    response = authenticated_client_for_user(records["admin"]).get("/api/v1/admin/reports/capacity/")

    assert response.status_code == 200
    by_course = {item["courseCode"]: item for item in response.json()["sections"]}
    assert by_course["CSC351"]["enrolledCount"] == 2
    assert by_course["CSC351"]["remainingSeats"] == 0
    assert by_course["CSC351"]["fillRate"] == 100
    assert by_course["CSC351"]["status"] == "Full"
    assert by_course["CSC352"]["remainingSeats"] == 1
    assert by_course["CSC352"]["fillRate"] == 80
    assert by_course["CSC352"]["status"] == "Near Capacity"
    assert by_course["CSC353"]["remainingSeats"] == 0
    assert by_course["CSC353"]["fillRate"] == 200
    assert by_course["CSC353"]["status"] == "Over Capacity"
    assert by_course["CSC354"]["status"] == "Open"


@pytest.mark.django_db
def test_grade_report_maps_existing_grade_statuses(settings):
    records = seed_reporting_data(settings)
    response = authenticated_client_for_user(records["admin"]).get("/api/v1/admin/reports/grades/")

    assert response.status_code == 200
    data = response.json()
    assert data["totals"]["draft"] == 1
    assert data["totals"]["official"] == 4
    assert data["totals"]["pendingApproval"] == 0
    assert data["statusBreakdown"] == [
        {"status": "DRAFT", "label": "Draft", "count": 1},
        {"status": "OFFICIAL", "label": "Official", "count": 4},
    ]
    section_full = next(item for item in data["sections"] if item["courseCode"] == "CSC351")
    assert section_full["draft"] == 1
    assert section_full["official"] == 1
    assert section_full["pendingApproval"] == 0
    assert section_full["completionRate"] == 50
    assert section_full["status"] == "Needs Review"


@pytest.mark.django_db
def test_moodle_sync_report_reuses_integration_data_safely(settings):
    records = seed_reporting_data(settings)
    response = authenticated_client_for_user(records["admin"]).get("/api/v1/admin/reports/moodle-sync/")

    assert response.status_code == 200
    data = response.json()
    assert data["outbox"] == {"pending": 1, "processed": 1, "failed": 1, "retryable": 2}
    assert data["mappings"] == {"users": 1, "courses": 1}
    assert data["latestFailedEvent"]["eventType"] == "GRADE_SYNC_REQUESTED"
    assert data["latestFailedEvent"]["lastError"] == "Moodle rejected token [REDACTED]"
    assert data["latestEngagementRun"]["status"] == records["run"].status
    assert data["recentIngestionFailures"][0]["lastError"] == "safe partial failure"
    body = json.dumps(data)
    assert "super-secret-token" not in body
    assert "wstoken" not in body


@pytest.mark.django_db
def test_calendar_and_activity_reports_return_operational_context(settings):
    records = seed_reporting_data(settings)
    client = authenticated_client_for_user(records["admin"])

    calendar_response = client.get("/api/v1/admin/reports/calendar/")
    activity_response = client.get("/api/v1/admin/reports/activity/")

    assert calendar_response.status_code == 200
    calendar = calendar_response.json()
    assert calendar["upcomingNext7Days"] == 2
    assert calendar["upcomingNext30Days"] == 3
    assert calendar["criticalDeadlines"] == 1
    assert calendar["registrationDeadlines"] == 1
    assert calendar["examPeriods"] == 1
    assert calendar["gradeSubmissionDeadlines"] == 1
    assert calendar["nextDeadline"]["title"] == "Registration deadline"

    assert activity_response.status_code == 200
    activity = activity_response.json()
    assert activity["unreadAdminNotifications"] == 1
    assert activity["auditEventsToday"] >= 2
    assert activity["auditWarnings"] >= 1
    assert activity["auditErrors"] >= 1
    assert any(item["label"] == "Failed Moodle sync events" and item["count"] == 1 for item in activity["riskIndicators"])
    assert any(item["label"] == "Active financial flags" and item["count"] == 1 for item in activity["riskIndicators"])


@pytest.mark.django_db
def test_capacity_csv_export_is_admin_only_secret_safe_and_audited(settings):
    records = seed_reporting_data(settings)
    client = authenticated_client_for_user(records["admin"])

    response = client.get("/api/v1/admin/reports/capacity/export.csv")

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    content = response.content.decode()
    assert "Course Code,Course Title,Section" in content
    assert "CSC351" in content
    assert "super-secret-token" not in content
    assert "wstoken" not in content
    assert AuditEvent.objects.filter(
        actor=records["admin"],
        category=AuditCategory.SYSTEM,
        action="ADMIN_REPORT_EXPORTED",
        target_type="AdminReport",
        target_id="capacity",
        severity=AuditSeverity.INFO,
    ).exists()
