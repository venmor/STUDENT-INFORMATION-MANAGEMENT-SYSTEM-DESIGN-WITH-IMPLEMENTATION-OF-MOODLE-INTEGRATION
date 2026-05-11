from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.accounts.constants import RoleCode
from apps.academics.models import Course, CourseSection
from apps.audit.models import AuditEvent
from apps.testutils import create_user


@pytest.mark.django_db
def test_seed_academic_calendar_demo_creates_safe_idempotent_events():
    create_user(username="calendar-demo-admin", primary_role=RoleCode.ADMIN, email="calendar-demo-admin@example.com")

    call_command("seed_academic_calendar_demo")
    call_command("seed_academic_calendar_demo")

    from apps.calendar.models import AcademicCalendarEvent

    events = AcademicCalendarEvent.objects.filter(metadata__demo=True)
    assert events.count() == 8
    assert set(events.values_list("event_type", flat=True)) == {
        "TERM_START",
        "REGISTRATION_OPEN",
        "REGISTRATION_DEADLINE",
        "DROP_DEADLINE",
        "ADVISING",
        "EXAM_PERIOD",
        "GRADE_SUBMISSION_DEADLINE",
        "TERM_END",
    }
    assert AuditEvent.objects.filter(action="ACADEMIC_CALENDAR_EVENTS_SYNCED", metadata__source="demo").count() == 1


@pytest.mark.django_db
def test_sync_academic_calendar_from_sections_creates_idempotent_deadline_events():
    faculty = create_user(
        username="calendar-section-faculty",
        email="calendar-section-faculty@example.com",
        primary_role=RoleCode.FACULTY,
    )
    course = Course.objects.create(
        course_code="CSC350",
        course_title="Distributed Systems",
        department="Computer Science",
        credit_hours=3,
        programme_code="BSc Computer Science",
        max_capacity=60,
    )
    now = timezone.now()
    section = CourseSection.objects.create(
        course=course,
        section_code="A",
        faculty_user=faculty,
        room="Lab 1",
        semester="Semester 1",
        academic_year="2026/2027",
        max_capacity=50,
        registration_opens_at=now + timedelta(days=1),
        registration_closes_at=now + timedelta(days=14),
        drop_deadline=now + timedelta(days=30),
    )

    call_command("sync_academic_calendar_from_sections")
    call_command("sync_academic_calendar_from_sections")

    from apps.calendar.models import AcademicCalendarEvent

    events = AcademicCalendarEvent.objects.filter(source="COURSE_SECTION", related_course_section=section)
    assert events.count() == 3
    assert set(events.values_list("event_type", flat=True)) == {
        "REGISTRATION_OPEN",
        "REGISTRATION_DEADLINE",
        "DROP_DEADLINE",
    }
    assert AuditEvent.objects.filter(action="ACADEMIC_CALENDAR_EVENTS_SYNCED", metadata__source="course_section").count() == 2
