from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
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
from apps.accounts.constants import RoleCode, STAFF_ROLE_CODES
from apps.accounts.models import User
from apps.integration.models import MoodleEngagementIngestionRun, MoodleEngagementIngestionStatus, MoodleEngagementSnapshot
from apps.students.models import AcademicStanding, FinancialFlag, StudentProfile


DEMO_PASSWORD = "DemoPass123!"


class Command(BaseCommand):
    help = "Seed safe repeatable demo data for Phase 4.1 analytics ETL."

    @transaction.atomic
    def handle(self, *args, **options):
        admin = self._upsert_user("analytics.admin", RoleCode.ADMIN, "analytics.admin@example.edu", "Analytics Admin")
        faculty = self._upsert_user("analytics.faculty", RoleCode.FACULTY, "analytics.faculty@example.edu", "Analytics Faculty")
        student_one = self._upsert_student(
            username="analytics.student1",
            full_name="Analytics Student One",
            student_number="2026/AI/001",
            standing=AcademicStanding.GOOD_STANDING,
            gpa=Decimal("3.45"),
        )
        student_two = self._upsert_student(
            username="analytics.student2",
            full_name="Analytics Student Two",
            student_number="2026/AI/002",
            standing=AcademicStanding.ACADEMIC_WARNING,
            gpa=Decimal("2.35"),
        )
        section = self._upsert_section(faculty=faculty)
        self._upsert_enrollment(student_one, section, admin)
        self._upsert_enrollment(student_two, section, admin)
        self._upsert_grades(student_one, student_two, section, faculty, admin)
        self._upsert_attendance(student_one, student_two, section, faculty)
        self._upsert_financial_flag(student_two, admin)
        self._upsert_moodle_snapshots(student_one, student_two, section)

        self.stdout.write(self.style.SUCCESS("Analytics demo data is ready."))
        self.stdout.write("Demo accounts use DemoPass123!. Run python manage.py run_analytics_etl to create snapshots.")

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

    def _upsert_student(self, *, username: str, full_name: str, student_number: str, standing: str, gpa: Decimal) -> StudentProfile:
        user = self._upsert_user(username, RoleCode.STUDENT, f"{username}@example.edu", full_name)
        student, _ = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                "student_number": student_number,
                "national_id": f"DEMO-{student_number}",
                "date_of_birth": date(2003, 1, 15),
                "gender": "Female",
                "programme": "BSc Computer Science",
                "year_of_study": 3,
            },
        )
        student.student_number = student_number
        student.national_id = f"DEMO-{student_number}"
        student.date_of_birth = date(2003, 1, 15)
        student.gender = "Female"
        student.programme = "BSc Computer Science"
        student.year_of_study = 3
        student.academic_standing = standing
        student.cumulative_gpa = gpa
        student.is_active = True
        student.save()
        return student

    def _upsert_section(self, *, faculty: User) -> CourseSection:
        course, _ = Course.objects.update_or_create(
            course_code="AIF410",
            defaults={
                "course_title": "AI Foundation Data Practices",
                "department": "Computer Science",
                "credit_hours": 3,
                "description": "Safe demo course for analytics ETL.",
                "programme_code": "BSc Computer Science",
                "max_capacity": 40,
                "is_active": True,
            },
        )
        now = timezone.now()
        section, _ = CourseSection.objects.update_or_create(
            course=course,
            section_code="A1",
            semester="Semester 1",
            academic_year="2026/2027",
            defaults={
                "faculty_user": faculty,
                "room": "Lab 4",
                "max_capacity": 40,
                "registration_opens_at": now - timedelta(days=30),
                "registration_closes_at": now + timedelta(days=7),
                "drop_deadline": now + timedelta(days=21),
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
                "reason": "Safe Phase 4.1 analytics demo enrollment.",
            },
        )

    def _upsert_grades(self, student_one: StudentProfile, student_two: StudentProfile, section: CourseSection, faculty: User, admin: User) -> None:
        GradeRecord.objects.update_or_create(
            student=student_one,
            section=section,
            defaults={
                "numeric_score": Decimal("82.00"),
                "letter_grade": "A",
                "grade_points": Decimal("4.00"),
                "grade_status": GradeStatus.OFFICIAL,
                "entered_by_user": faculty,
                "officialised_by_user": admin,
                "officialised_at": timezone.now(),
            },
        )
        GradeRecord.objects.update_or_create(
            student=student_two,
            section=section,
            defaults={
                "numeric_score": Decimal("65.00"),
                "letter_grade": "C",
                "grade_points": Decimal("2.00"),
                "grade_status": GradeStatus.DRAFT,
                "entered_by_user": faculty,
                "officialised_by_user": None,
                "officialised_at": None,
            },
        )

    def _upsert_attendance(self, student_one: StudentProfile, student_two: StudentProfile, section: CourseSection, faculty: User) -> None:
        for offset, first_status, second_status in ((0, AttendanceStatus.PRESENT, AttendanceStatus.PRESENT), (1, AttendanceStatus.PRESENT, AttendanceStatus.ABSENT)):
            session, _ = AttendanceSession.objects.get_or_create(
                section=section,
                session_date=timezone.localdate() - timedelta(days=offset),
                defaults={"recorded_by_user": faculty},
            )
            AttendanceRecord.objects.update_or_create(attendance_session=session, student=student_one, defaults={"status": first_status})
            AttendanceRecord.objects.update_or_create(attendance_session=session, student=student_two, defaults={"status": second_status})

    def _upsert_financial_flag(self, student: StudentProfile, admin: User) -> None:
        FinancialFlag.objects.update_or_create(
            student=student,
            flag_type="REGISTRATION_HOLD",
            defaults={
                "reason": "Safe demo active hold for analytics counts.",
                "effective_date": timezone.localdate(),
                "cleared_date": None,
                "created_by_user": admin,
            },
        )

    def _upsert_moodle_snapshots(self, student_one: StudentProfile, student_two: StudentProfile, section: CourseSection) -> None:
        run = MoodleEngagementIngestionRun.objects.filter(summary_payload__demo_key="phase_4_1_analytics").first()
        if run is None:
            run = MoodleEngagementIngestionRun.objects.create(
                status=MoodleEngagementIngestionStatus.SUCCEEDED,
                completed_at=timezone.now(),
                summary_payload={"demo_key": "phase_4_1_analytics"},
            )
        else:
            run.status = MoodleEngagementIngestionStatus.SUCCEEDED
            run.completed_at = timezone.now()
            run.summary_payload = {"demo_key": "phase_4_1_analytics"}
            run.save(update_fields=["status", "completed_at", "summary_payload"])
        for index, student in enumerate((student_one, student_two), start=1):
            MoodleEngagementSnapshot.objects.update_or_create(
                run=run,
                moodle_user_id=9000 + index,
                moodle_course_id=8000,
                defaults={
                    "user": student.user,
                    "student": student,
                    "section": section,
                    "moodle_last_access_at": timezone.now() - timedelta(hours=index),
                    "moodle_course_last_access_at": timezone.now() - timedelta(minutes=30 * index),
                    "collected_at": timezone.now(),
                    "raw_summary": {"demo": True, "safe": True},
                },
            )
