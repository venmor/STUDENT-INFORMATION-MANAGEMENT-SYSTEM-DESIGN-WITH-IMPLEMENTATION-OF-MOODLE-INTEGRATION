from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.accounts.constants import RoleCode
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
    SpecialGradeCode,
)
from apps.integration.models import (
    MoodleEngagementIngestionRun,
    MoodleEngagementIngestionStatus,
    MoodleEngagementSnapshot,
)
from apps.students.models import AcademicStanding, FinancialFlag, StudentProfile
from apps.testutils import create_user

from apps.atrisk.signals import evaluate_all_signals


pytestmark = pytest.mark.django_db


@pytest.fixture
def faculty():
    return create_user(username="atrisk.t.faculty", primary_role=RoleCode.FACULTY, email="atrisk.t.fac@example.edu")


@pytest.fixture
def student():
    user = create_user(username="atrisk.t.student1", primary_role=RoleCode.STUDENT, email="atrisk1@example.edu")
    return StudentProfile.objects.create(
        user=user,
        student_number="2026/TSTR/001",
        national_id="NRC-TSTR-001",
        date_of_birth=date(2003, 3, 15),
        gender="Female",
        programme="BSc Computer Science",
        year_of_study=2,
        academic_standing=AcademicStanding.GOOD_STANDING,
        cumulative_gpa=Decimal("3.20"),
        is_active=True,
    )


@pytest.fixture
def course_and_section(faculty):
    now = timezone.now()
    course = Course.objects.create(
        course_code="TSIG201",
        course_title="Data Structures",
        department="Computer Science",
        credit_hours=3,
    )
    section = CourseSection.objects.create(
        course=course,
        section_code="A",
        semester="Semester 1",
        academic_year="2025/2026",
        status=CourseSectionStatus.ACTIVE,
        faculty_user=faculty,
        max_capacity=30,
        room="LH101",
        registration_opens_at=now - timedelta(days=90),
        registration_closes_at=now - timedelta(days=60),
        drop_deadline=now - timedelta(days=30),
    )
    return course, section


def test_attendance_flag_triggers_when_below_threshold(student, faculty, course_and_section):
    _, section = course_and_section
    Enrollment.objects.create(
        student=student, section=section,
        enrollment_status=EnrollmentStatus.ENROLLED, actor_role="ADMIN",
    )
    # Create multiple sessions: 1 present + 4 absent = 20% attendance
    # UniqueConstraint on (attendance_session, student), so 1 record per session
    for i in range(5):
        session = AttendanceSession.objects.create(
            section=section, session_date=date.today() - timedelta(days=i),
            recorded_by_user=faculty,
        )
        status = AttendanceStatus.PRESENT if i == 0 else AttendanceStatus.ABSENT
        AttendanceRecord.objects.create(student=student, attendance_session=session, status=status)

    results = evaluate_all_signals(student)
    assert results["attendance_flag"] is True


def test_attendance_flag_does_not_trigger_when_above_threshold(student, faculty, course_and_section):
    _, section = course_and_section
    Enrollment.objects.create(
        student=student, section=section,
        enrollment_status=EnrollmentStatus.ENROLLED, actor_role="ADMIN",
    )
    # Create multiple sessions: 4 present + 1 absent = 80% attendance
    for i in range(5):
        session = AttendanceSession.objects.create(
            section=section, session_date=date.today() - timedelta(days=i),
            recorded_by_user=faculty,
        )
        status = AttendanceStatus.ABSENT if i == 0 else AttendanceStatus.PRESENT
        AttendanceRecord.objects.create(student=student, attendance_session=session, status=status)

    results = evaluate_all_signals(student)
    assert results["attendance_flag"] is False


def test_academic_probation_triggers(student):
    student.academic_standing = AcademicStanding.PROBATION
    student.save()

    results = evaluate_all_signals(student)
    assert results["academic_probation"] is True


def test_academic_probation_does_not_trigger_for_good_standing(student):
    results = evaluate_all_signals(student)
    assert results["academic_probation"] is False


def test_financial_hold_triggers(student, faculty):
    FinancialFlag.objects.create(
        student=student,
        flag_type="TUITION_OVERDUE",
        reason="Outstanding fees",
        effective_date=date.today(),
        created_by_user=faculty,
    )

    results = evaluate_all_signals(student)
    assert results["financial_hold"] is True


def test_financial_hold_does_not_trigger_when_cleared(student, faculty):
    FinancialFlag.objects.create(
        student=student,
        flag_type="TUITION_OVERDUE",
        reason="Outstanding fees",
        effective_date=date.today() - timedelta(days=30),
        cleared_date=date.today() - timedelta(days=5),
        created_by_user=faculty,
    )

    results = evaluate_all_signals(student)
    assert results["financial_hold"] is False


def test_grade_decline_does_not_trigger_without_snapshots(student):
    # Without analytics snapshots, no decline is detectable
    results = evaluate_all_signals(student)
    assert results["grade_decline"] is False


def test_incomplete_grade_triggers(student, faculty, course_and_section):
    _, section = course_and_section
    GradeRecord.objects.create(
        student=student, section=section, grade_status=GradeStatus.OFFICIAL,
        special_code=SpecialGradeCode.INCOMPLETE, entered_by_user=faculty,
    )
    # Need a second section for second incomplete
    now = timezone.now()
    course2 = Course.objects.create(
        course_code="TSIG202", course_title="Algorithms",
        department="Computer Science", credit_hours=3,
    )
    section2 = CourseSection.objects.create(
        course=course2, section_code="A", semester="Semester 1", academic_year="2025/2026",
        status=CourseSectionStatus.ACTIVE, faculty_user=faculty, max_capacity=30,
        room="LH102",
        registration_opens_at=now - timedelta(days=90),
        registration_closes_at=now - timedelta(days=60),
        drop_deadline=now - timedelta(days=30),
    )
    GradeRecord.objects.create(
        student=student, section=section2, grade_status=GradeStatus.OFFICIAL,
        special_code=SpecialGradeCode.INCOMPLETE, entered_by_user=faculty,
    )

    results = evaluate_all_signals(student)
    assert results["incomplete_grade"] is True


def test_moodle_inactivity_triggers(student):
    run = MoodleEngagementIngestionRun.objects.create(status=MoodleEngagementIngestionStatus.SUCCEEDED)
    MoodleEngagementSnapshot.objects.create(
        run=run,
        student=student,
        moodle_user_id=1001,
        moodle_course_id=2001,
        moodle_last_access_at=timezone.now() - timedelta(days=20),
        collected_at=timezone.now(),
    )

    results = evaluate_all_signals(student)
    assert results["moodle_inactivity"] is True


def test_moodle_inactivity_does_not_trigger_with_recent_access(student):
    run = MoodleEngagementIngestionRun.objects.create(status=MoodleEngagementIngestionStatus.SUCCEEDED)
    MoodleEngagementSnapshot.objects.create(
        run=run,
        student=student,
        moodle_user_id=1001,
        moodle_course_id=2001,
        moodle_last_access_at=timezone.now() - timedelta(days=3),
        collected_at=timezone.now(),
    )

    results = evaluate_all_signals(student)
    assert results["moodle_inactivity"] is False


def test_quiz_failure_pattern_triggers(student):
    run = MoodleEngagementIngestionRun.objects.create(status=MoodleEngagementIngestionStatus.SUCCEEDED)
    MoodleEngagementSnapshot.objects.create(
        run=run,
        student=student,
        moodle_user_id=1001,
        moodle_course_id=2001,
        quiz_average=Decimal("35.00"),
        quiz_attempt_count=5,
        collected_at=timezone.now(),
    )

    results = evaluate_all_signals(student)
    assert results["quiz_failure_pattern"] is True


def test_quiz_failure_does_not_trigger_above_threshold(student):
    run = MoodleEngagementIngestionRun.objects.create(status=MoodleEngagementIngestionStatus.SUCCEEDED)
    MoodleEngagementSnapshot.objects.create(
        run=run,
        student=student,
        moodle_user_id=1001,
        moodle_course_id=2001,
        quiz_average=Decimal("65.00"),
        quiz_attempt_count=5,
        collected_at=timezone.now(),
    )

    results = evaluate_all_signals(student)
    assert results["quiz_failure_pattern"] is False


def test_forum_disengagement_triggers(student):
    run = MoodleEngagementIngestionRun.objects.create(status=MoodleEngagementIngestionStatus.SUCCEEDED)
    MoodleEngagementSnapshot.objects.create(
        run=run,
        student=student,
        moodle_user_id=1001,
        moodle_course_id=2001,
        forum_post_count=0,
        moodle_course_last_access_at=timezone.now() - timedelta(days=25),
        collected_at=timezone.now(),
    )

    results = evaluate_all_signals(student)
    assert results["forum_disengagement"] is True


def test_forum_disengagement_does_not_trigger_with_recent_access(student):
    run = MoodleEngagementIngestionRun.objects.create(status=MoodleEngagementIngestionStatus.SUCCEEDED)
    MoodleEngagementSnapshot.objects.create(
        run=run,
        student=student,
        moodle_user_id=1001,
        moodle_course_id=2001,
        forum_post_count=0,
        moodle_course_last_access_at=timezone.now() - timedelta(days=5),
        collected_at=timezone.now(),
    )

    results = evaluate_all_signals(student)
    assert results["forum_disengagement"] is False


def test_no_signals_for_clean_student(student):
    results = evaluate_all_signals(student)
    active = [k for k, v in results.items() if v]
    assert active == []
