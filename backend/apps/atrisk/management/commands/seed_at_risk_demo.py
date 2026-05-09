from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
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
    SpecialGradeCode,
)
from apps.accounts.constants import RoleCode
from apps.accounts.models import Role, User
from apps.atrisk.services import run_at_risk_engine
from apps.integration.models import (
    MoodleEngagementIngestionRun,
    MoodleEngagementIngestionStatus,
    MoodleEngagementSnapshot,
)
from apps.students.models import AcademicStanding, FinancialFlag, StudentProfile


class Command(BaseCommand):
    help = "Seed demo students with various at-risk signal patterns to trigger all severity levels."

    def handle(self, *args, **options):
        Role.objects.get_or_create(code=RoleCode.ADVISOR, defaults={"name": "Advisor"})
        Role.objects.get_or_create(code=RoleCode.STUDENT, defaults={"name": "Student"})
        Role.objects.get_or_create(code=RoleCode.FACULTY, defaults={"name": "Faculty"})

        faculty = self._get_or_create_user("atrisk.faculty", RoleCode.FACULTY, "At-Risk Demo Faculty")
        advisor = self._get_or_create_user("atrisk.advisor", RoleCode.ADVISOR, "At-Risk Demo Advisor")

        course, section = self._get_or_create_course(faculty)

        # HIGH severity student: Academic probation (triggers HIGH weight signal)
        s1 = self._get_or_create_student(
            "atrisk.high1", "2026/RISK/H01", AcademicStanding.PROBATION, Decimal("1.60")
        )
        self.stdout.write(f"  Created/verified HIGH student (probation): {s1.student_number}")

        # HIGH severity student: Low attendance (<75%)
        s2 = self._get_or_create_student(
            "atrisk.high2", "2026/RISK/H02", AcademicStanding.GOOD_STANDING, Decimal("2.70")
        )
        self._create_attendance_records(s2, section, faculty, present=2, absent=8)
        self.stdout.write(f"  Created/verified HIGH student (low attendance): {s2.student_number}")

        # MEDIUM severity student: financial hold + quiz failure (2 medium signals)
        s3 = self._get_or_create_student(
            "atrisk.med1", "2026/RISK/M01", AcademicStanding.GOOD_STANDING, Decimal("2.90")
        )
        self._create_financial_flag(s3, advisor)
        self._create_moodle_snapshot(s3, days_since_login=5, quiz_avg=Decimal("35.00"), forum_posts=2)
        self.stdout.write(f"  Created/verified MEDIUM student (financial + quiz): {s3.student_number}")

        # LOW severity student: forum disengagement only
        s4 = self._get_or_create_student(
            "atrisk.low1", "2026/RISK/L01", AcademicStanding.GOOD_STANDING, Decimal("3.40")
        )
        self._create_moodle_snapshot(
            s4, days_since_login=5, quiz_avg=Decimal("70.00"), forum_posts=0, course_last_access_days=25
        )
        self.stdout.write(f"  Created/verified LOW student (forum disengagement): {s4.student_number}")

        # CLEAN student: No signals
        s5 = self._get_or_create_student(
            "atrisk.clean", "2026/RISK/C01", AcademicStanding.GOOD_STANDING, Decimal("3.80")
        )
        self.stdout.write(f"  Created/verified CLEAN student (no signals): {s5.student_number}")

        # Run the engine
        self.stdout.write("\nRunning at-risk engine on demo data...")
        stats = run_at_risk_engine()
        self.stdout.write(self.style.SUCCESS(
            f"At-risk demo seeded: {stats['students_processed']} processed, "
            f"{stats['alerts_created']} alerts created."
        ))

    def _get_or_create_user(self, username: str, role: str, full_name: str) -> User:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"primary_role": role, "full_name": full_name},
        )
        if created or not user.has_usable_password():
            user.set_password("DemoPass123!")
            user.save()
        return user

    def _get_or_create_student(
        self, username: str, student_number: str, standing: str, gpa: Decimal
    ) -> StudentProfile:
        user = self._get_or_create_user(username, RoleCode.STUDENT, username.replace(".", " ").title())
        student, _ = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                "student_number": student_number,
                "national_id": f"NRC-{student_number.replace('/', '-')}",
                "date_of_birth": date(2003, 1, 15),
                "gender": "Male",
                "programme": "BSc Computer Science",
                "year_of_study": 2,
                "academic_standing": standing,
                "cumulative_gpa": gpa,
                "is_active": True,
            },
        )
        # Ensure standing is up to date
        if student.academic_standing != standing:
            student.academic_standing = standing
            student.save(update_fields=["academic_standing"])
        return student

    def _get_or_create_course(self, faculty):
        now = timezone.now()
        course, _ = Course.objects.get_or_create(
            course_code="RISK101",
            defaults={
                "course_title": "Risk Demo Course",
                "department": "Computer Science",
                "credit_hours": 3,
            },
        )
        section, _ = CourseSection.objects.get_or_create(
            course=course,
            section_code="A",
            semester="Semester 1",
            academic_year="2025/2026",
            defaults={
                "status": CourseSectionStatus.ACTIVE,
                "faculty_user": faculty,
                "max_capacity": 50,
                "room": "LH101",
                "registration_opens_at": now - timedelta(days=90),
                "registration_closes_at": now - timedelta(days=60),
                "drop_deadline": now - timedelta(days=30),
            },
        )
        return course, section

    def _create_financial_flag(self, student, advisor):
        if not FinancialFlag.objects.filter(student=student, cleared_date__isnull=True).exists():
            FinancialFlag.objects.create(
                student=student,
                flag_type="TUITION_OVERDUE",
                reason="Outstanding tuition fees",
                effective_date=date.today() - timedelta(days=30),
                created_by_user=advisor,
            )

    def _create_moodle_snapshot(
        self,
        student,
        *,
        days_since_login: int,
        quiz_avg: Decimal,
        forum_posts: int,
        course_last_access_days: int | None = None,
    ):
        if MoodleEngagementSnapshot.objects.filter(student=student).exists():
            return
        run, _ = MoodleEngagementIngestionRun.objects.get_or_create(
            status=MoodleEngagementIngestionStatus.SUCCEEDED,
            defaults={"completed_at": timezone.now()},
        )
        course_access = timezone.now() - timedelta(days=course_last_access_days or days_since_login)
        MoodleEngagementSnapshot.objects.create(
            run=run,
            student=student,
            moodle_user_id=abs(hash(student.student_number)) % 100000,
            moodle_course_id=3001,
            moodle_last_access_at=timezone.now() - timedelta(days=days_since_login),
            moodle_course_last_access_at=course_access,
            quiz_average=quiz_avg,
            quiz_attempt_count=5,
            forum_post_count=forum_posts,
            assignment_submission_count=10,
            assignment_submission_rate=Decimal("80.00"),
            collected_at=timezone.now(),
        )

    def _create_attendance_records(self, student, section, faculty, present: int, absent: int):
        if AttendanceRecord.objects.filter(student=student).exists():
            return
        Enrollment.objects.get_or_create(
            student=student,
            section=section,
            defaults={"enrollment_status": EnrollmentStatus.ENROLLED, "actor_role": "ADMIN"},
        )
        # UniqueConstraint on (attendance_session, student): one record per session
        total = present + absent
        for i in range(total):
            session = AttendanceSession.objects.create(
                section=section,
                session_date=date.today() - timedelta(days=i),
                recorded_by_user=faculty,
            )
            status = AttendanceStatus.PRESENT if i < present else AttendanceStatus.ABSENT
            AttendanceRecord.objects.create(
                student=student, attendance_session=session, status=status
            )
