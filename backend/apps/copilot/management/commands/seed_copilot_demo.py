from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.academics.models import Course, CourseSection, CourseSectionStatus, Enrollment, EnrollmentStatus, GradeRecord, GradeStatus
from apps.accounts.constants import RoleCode, STAFF_ROLE_CODES
from apps.accounts.models import User
from apps.analytics.services import run_analytics_etl
from apps.calendar.services import seed_demo_events
from apps.copilot.models import CopilotMessageRole
from apps.copilot.services import answer_copilot_question, create_copilot_session
from apps.knowledge.services import ingest_knowledge_base, seed_demo_knowledge_sources
from apps.students.models import AcademicStanding, StudentProfile


DEMO_PASSWORD = "DemoPass123!"


class Command(BaseCommand):
    help = "Seed safe repeatable demo data for Phase 4.2 student co-pilot."

    @transaction.atomic
    def handle(self, *args, **options):
        admin = self._upsert_user("admin.demo", RoleCode.ADMIN, "admin.demo@example.edu", "Admin Demo")
        faculty = self._upsert_user("faculty.demo", RoleCode.FACULTY, "faculty.demo@example.edu", "Faculty Demo")
        student = self._upsert_student()
        section = self._upsert_course_section(faculty)
        self._upsert_enrollment(student, section, admin)
        self._upsert_grade(student, section, faculty, admin)
        seed_demo_events(actor=admin)
        run_analytics_etl(student_id=student.id, academic_year="2026/2027", semester="Semester 1", actor=admin)
        seed_demo_knowledge_sources(created_by=admin)
        ingest_knowledge_base(rebuild=True, actor=admin)

        session = student.copilot_sessions.filter(title="Phase 4.2 demo questions").first()
        if session is None:
            session = create_copilot_session(user=student.user, title="Phase 4.2 demo questions")
        if not session.messages.filter(role=CopilotMessageRole.ASSISTANT).exists():
            answer_copilot_question(
                user=student.user,
                question="What is the deadline to drop a course?",
                session_id=session.id,
            )

        self.stdout.write(self.style.SUCCESS("Co-pilot demo data is ready."))
        self.stdout.write(f"Demo login: student.demo1 / {DEMO_PASSWORD}")
        self.stdout.write(f"Session: {session.id}")
        self.stdout.write("Run python manage.py test_copilot_query \"What is the deadline to drop a course?\"")

    def _upsert_user(self, username: str, role: str, email: str, full_name: str) -> User:
        user, _ = User.objects.get_or_create(username=username)
        user.email = email
        user.full_name = full_name
        user.primary_role = role
        user.is_active = True
        user.is_staff = role in STAFF_ROLE_CODES
        user.must_reset_password = False
        user.set_password(DEMO_PASSWORD)
        user.save()
        return user

    def _upsert_student(self) -> StudentProfile:
        user = self._upsert_user("student.demo1", RoleCode.STUDENT, "student.demo1@example.edu", "Temba Mwansa")
        student, _ = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                "student_number": "2026/CS/001",
                "national_id": "111111/11/1",
                "date_of_birth": date(2003, 2, 14),
                "gender": "Male",
                "programme": "BSc Computer Science",
                "year_of_study": 4,
                "academic_standing": AcademicStanding.GOOD_STANDING,
            },
        )
        student.student_number = "2026/CS/001"
        student.national_id = "111111/11/1"
        student.date_of_birth = date(2003, 2, 14)
        student.gender = "Male"
        student.programme = "BSc Computer Science"
        student.year_of_study = 4
        student.academic_standing = AcademicStanding.GOOD_STANDING
        student.cumulative_gpa = Decimal("3.20")
        student.is_active = True
        student.save()
        return student

    def _upsert_course_section(self, faculty: User) -> CourseSection:
        course, _ = Course.objects.update_or_create(
            course_code="CSC410",
            defaults={
                "course_title": "Distributed Systems",
                "department": "Computer Science",
                "credit_hours": 3,
                "description": "Demo enrolled course for co-pilot context.",
                "programme_code": "BSc Computer Science",
                "max_capacity": 80,
                "is_active": True,
            },
        )
        section, _ = CourseSection.objects.update_or_create(
            course=course,
            section_code="A1",
            semester="Semester 1",
            academic_year="2026/2027",
            defaults={
                "faculty_user": faculty,
                "room": "LT-4",
                "max_capacity": 80,
                "registration_opens_at": timezone.now() - timedelta(days=14),
                "registration_closes_at": timezone.now() + timedelta(days=14),
                "drop_deadline": timezone.now() + timedelta(days=28),
                "attendance_threshold": Decimal("75.00"),
                "status": CourseSectionStatus.ACTIVE,
            },
        )
        return section

    def _upsert_enrollment(self, student: StudentProfile, section: CourseSection, admin: User) -> None:
        Enrollment.objects.update_or_create(
            student=student,
            section=section,
            defaults={
                "enrollment_status": EnrollmentStatus.ENROLLED,
                "actor_role": RoleCode.ADMIN,
                "actor_user": admin,
                "is_active": True,
                "reason": "Safe Phase 4.2 co-pilot demo enrollment.",
            },
        )

    def _upsert_grade(self, student: StudentProfile, section: CourseSection, faculty: User, admin: User) -> None:
        GradeRecord.objects.update_or_create(
            student=student,
            section=section,
            defaults={
                "numeric_score": Decimal("84.00"),
                "letter_grade": "A",
                "grade_points": Decimal("4.00"),
                "grade_status": GradeStatus.OFFICIAL,
                "entered_by_user": faculty,
                "officialised_by_user": admin,
                "officialised_at": timezone.now(),
            },
        )
