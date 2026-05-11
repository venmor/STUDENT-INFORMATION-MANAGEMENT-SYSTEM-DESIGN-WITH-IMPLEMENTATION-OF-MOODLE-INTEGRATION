from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.academics.models import (
    AttendanceRecord,
    AttendanceSession,
    AttendanceStatus,
    Course,
    CourseSection,
    CourseSectionStatus,
    Enrollment,
    EnrollmentStatus,
    GradeRecord,
    GradeStatus,
)
from apps.accounts.constants import RoleCode
from apps.analytics.models import AnalyticsETLRunStatus, StudentAnalyticsSnapshot
from apps.analytics.services import run_analytics_etl
from apps.integration.models import MoodleEngagementIngestionRun, MoodleEngagementIngestionStatus, MoodleEngagementSnapshot
from apps.students.models import AcademicStanding, FinancialFlag, StudentProfile
from apps.testutils import create_user


pytestmark = pytest.mark.django_db


def create_student_with_section():
    admin = create_user(username="analytics-admin", primary_role=RoleCode.ADMIN, email="analytics-admin@example.com")
    faculty = create_user(username="analytics-faculty", primary_role=RoleCode.FACULTY, email="analytics-faculty@example.com")
    student_user = create_user(username="analytics-student", primary_role=RoleCode.STUDENT, email="analytics-student@example.com")
    student = StudentProfile.objects.create(
        user=student_user,
        student_number="2026/AN/001",
        national_id="AN-001",
        date_of_birth=timezone.localdate() - timedelta(days=365 * 20),
        gender="Female",
        programme="BSc Computer Science",
        year_of_study=3,
        academic_standing=AcademicStanding.ACADEMIC_WARNING,
        cumulative_gpa=Decimal("3.25"),
        is_active=True,
    )
    course = Course.objects.create(
        course_code="CSC410",
        course_title="Data Foundations",
        department="Computer Science",
        credit_hours=3,
        programme_code="BSc Computer Science",
        max_capacity=40,
    )
    now = timezone.now()
    section = CourseSection.objects.create(
        course=course,
        section_code="A1",
        faculty_user=faculty,
        room="Lab 1",
        semester="Semester 1",
        academic_year="2026/2027",
        max_capacity=40,
        registration_opens_at=now - timedelta(days=20),
        registration_closes_at=now + timedelta(days=10),
        drop_deadline=now + timedelta(days=20),
        attendance_threshold=Decimal("75.00"),
        status=CourseSectionStatus.ACTIVE,
    )
    Enrollment.objects.create(
        student=student,
        section=section,
        enrollment_status=EnrollmentStatus.ENROLLED,
        actor_role=RoleCode.ADMIN,
        actor_user=admin,
        is_active=True,
    )
    GradeRecord.objects.create(
        student=student,
        section=section,
        numeric_score=Decimal("80.00"),
        letter_grade="A",
        grade_points=Decimal("4.00"),
        grade_status=GradeStatus.OFFICIAL,
        entered_by_user=faculty,
        officialised_by_user=admin,
        officialised_at=now,
    )
    draft_course = Course.objects.create(
        course_code="CSC411",
        course_title="Analytics Workshop",
        department="Computer Science",
        credit_hours=3,
        programme_code="BSc Computer Science",
        max_capacity=40,
    )
    draft_section = CourseSection.objects.create(
        course=draft_course,
        section_code="A1",
        faculty_user=faculty,
        room="Lab 2",
        semester="Semester 1",
        academic_year="2026/2027",
        max_capacity=40,
        registration_opens_at=now - timedelta(days=20),
        registration_closes_at=now + timedelta(days=10),
        drop_deadline=now + timedelta(days=20),
        attendance_threshold=Decimal("75.00"),
        status=CourseSectionStatus.ACTIVE,
    )
    GradeRecord.objects.create(
        student=student,
        section=draft_section,
        numeric_score=Decimal("70.00"),
        letter_grade="B",
        grade_points=Decimal("3.00"),
        grade_status=GradeStatus.DRAFT,
        entered_by_user=faculty,
    )
    first_attendance_session = AttendanceSession.objects.create(section=section, session_date=timezone.localdate(), recorded_by_user=faculty)
    attendance_session = AttendanceSession.objects.create(
        section=section,
        session_date=timezone.localdate() - timedelta(days=1),
        recorded_by_user=faculty,
    )
    AttendanceRecord.objects.create(attendance_session=attendance_session, student=student, status=AttendanceStatus.PRESENT)
    AttendanceRecord.objects.create(
        attendance_session=first_attendance_session,
        student=student,
        status=AttendanceStatus.ABSENT,
    )
    FinancialFlag.objects.create(
        student=student,
        flag_type="REGISTRATION_HOLD",
        reason="Safe analytics test flag",
        effective_date=timezone.localdate(),
        created_by_user=admin,
    )
    run = MoodleEngagementIngestionRun.objects.create(status=MoodleEngagementIngestionStatus.SUCCEEDED)
    MoodleEngagementSnapshot.objects.create(
        run=run,
        user=student_user,
        student=student,
        section=section,
        moodle_user_id=101,
        moodle_course_id=202,
        moodle_last_access_at=now - timedelta(hours=6),
        moodle_course_last_access_at=now - timedelta(hours=3),
        collected_at=now,
    )
    return student


def test_analytics_etl_creates_snapshot_from_existing_sis_and_moodle_data():
    student = create_student_with_section()

    run = run_analytics_etl(academic_year="2026/2027", semester="Semester 1")

    assert run.status == AnalyticsETLRunStatus.SUCCEEDED
    assert run.students_processed == 1
    assert run.snapshots_created == 1
    assert run.moodle_snapshots_used == 1
    snapshot = StudentAnalyticsSnapshot.objects.get(student=student)
    assert snapshot.programme == "BSc Computer Science"
    assert snapshot.academic_standing == AcademicStanding.ACADEMIC_WARNING
    assert snapshot.active_enrollment_count == 1
    assert snapshot.official_grade_count == 1
    assert snapshot.draft_grade_count == 1
    assert snapshot.financial_flag_count == 1
    assert snapshot.attendance_average == Decimal("50.00")
    assert snapshot.gpa == Decimal("3.25")
    assert snapshot.latest_moodle_course_access_at is not None
    assert "national_id" not in snapshot.metadata


def test_analytics_etl_dry_run_records_run_without_writing_snapshots():
    create_student_with_section()

    run = run_analytics_etl(academic_year="2026/2027", semester="Semester 1", dry_run=True)

    assert run.status == AnalyticsETLRunStatus.SUCCEEDED
    assert run.dry_run is True
    assert run.students_processed == 1
    assert run.snapshots_created == 0
    assert StudentAnalyticsSnapshot.objects.count() == 0


def test_analytics_etl_handles_missing_optional_data_as_null_or_zero():
    user = create_user(username="analytics-empty-student", primary_role=RoleCode.STUDENT, email="analytics-empty@example.com")
    student = StudentProfile.objects.create(
        user=user,
        student_number="2026/AN/002",
        national_id="AN-002",
        date_of_birth=timezone.localdate() - timedelta(days=365 * 19),
        gender="Male",
        programme="BSc Information Systems",
        year_of_study=1,
        cumulative_gpa=Decimal("0.00"),
        is_active=True,
    )

    run = run_analytics_etl(academic_year="2026/2027", semester="Semester 1", student_id=student.id)

    snapshot = StudentAnalyticsSnapshot.objects.get(student=student)
    assert run.failure_count == 0
    assert snapshot.attendance_average is None
    assert snapshot.active_enrollment_count == 0
    assert snapshot.financial_flag_count == 0
    assert snapshot.moodle_snapshot_count == 0
    assert snapshot.latest_moodle_access_at is None
