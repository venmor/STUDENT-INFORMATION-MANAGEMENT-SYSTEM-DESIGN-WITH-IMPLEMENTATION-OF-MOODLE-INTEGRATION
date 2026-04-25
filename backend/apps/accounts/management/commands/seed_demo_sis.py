from __future__ import annotations

from datetime import date, time, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.constants import CapabilityName, RoleCode, STAFF_ROLE_CODES
from apps.accounts.models import User, UserCapability
from apps.academics.models import (
    AcademicStandingRule,
    AttendanceRecord,
    AttendanceSession,
    AttendanceStatus,
    Course,
    CourseSection,
    CourseSectionStatus,
    Enrollment,
    EnrollmentStatus,
    GradeRecord,
    GradingScaleBand,
    GradeStatus,
    SectionTimetable,
)
from apps.academics.services import create_enrollment, officialise_grade, record_grade
from apps.students.models import (
    AcademicStanding,
    AdvisorAssignment,
    AdvisingNote,
    AdvisingNoteStatus,
    FinancialFlag,
    StudentCorrectionRequest,
    StudentCorrectionRequestStatus,
    StudentProfile,
)


class Command(BaseCommand):
    help = "Seed repeatable demo data for local Student Information System testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="DemoPass123!",
            help="Password applied to all demo accounts. Default: DemoPass123!",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not GradingScaleBand.objects.exists() or not AcademicStandingRule.objects.exists():
            raise CommandError("Academic defaults are missing. Run migrations before seeding demo data.")

        password = options["password"]
        today = timezone.localdate()
        now = timezone.now()

        admin_user = self._upsert_user(
            username="admin.demo",
            email="admin.demo@example.edu",
            full_name="Admin Demo",
            primary_role=RoleCode.ADMIN,
            password=password,
        )
        advisor_user = self._upsert_user(
            username="advisor.demo",
            email="advisor.demo@example.edu",
            full_name="Advisor Demo",
            primary_role=RoleCode.ADVISOR,
            password=password,
        )
        faculty_user = self._upsert_user(
            username="faculty.demo",
            email="faculty.demo@example.edu",
            full_name="Faculty Demo",
            primary_role=RoleCode.FACULTY,
            password=password,
        )
        student_one_user = self._upsert_user(
            username="student.demo1",
            email="student.demo1@example.edu",
            full_name="Temba Mwansa",
            primary_role=RoleCode.STUDENT,
            password=password,
        )
        student_two_user = self._upsert_user(
            username="student.demo2",
            email="student.demo2@example.edu",
            full_name="Mwila Chanda",
            primary_role=RoleCode.STUDENT,
            password=password,
        )

        UserCapability.objects.update_or_create(
            user=admin_user,
            capability_name=CapabilityName.WELLBEING_COORDINATOR,
        )

        student_one = self._upsert_student_profile(
            user=student_one_user,
            student_number="2026/CS/001",
            national_id="111111/11/1",
            date_of_birth=date(2003, 2, 14),
            gender="Male",
            programme="BSc Computer Science",
            year_of_study=4,
            academic_standing=AcademicStanding.GOOD_STANDING,
        )
        student_two = self._upsert_student_profile(
            user=student_two_user,
            student_number="2026/CS/002",
            national_id="222222/22/2",
            date_of_birth=date(2003, 8, 21),
            gender="Female",
            programme="BSc Computer Science",
            year_of_study=4,
            academic_standing=AcademicStanding.ACADEMIC_WARNING,
        )

        self._upsert_assignment(student_one, advisor_user, today)
        self._upsert_assignment(student_two, advisor_user, today)

        current_course = self._upsert_course(
            course_code="CSC410",
            course_title="Distributed Systems",
            department="Computer Science",
            credit_hours=3,
            description="Advanced distributed systems concepts for final-year delivery.",
            programme_code="BSC-CS",
            max_capacity=80,
        )
        current_course_two = self._upsert_course(
            course_code="CSC420",
            course_title="Information Security",
            department="Computer Science",
            credit_hours=3,
            description="Applied security controls and governance for information systems.",
            programme_code="BSC-CS",
            max_capacity=80,
        )
        historical_course = self._upsert_course(
            course_code="CSC305",
            course_title="Software Engineering",
            department="Computer Science",
            credit_hours=3,
            description="Historical completed course used for transcript and GPA testing.",
            programme_code="BSC-CS",
            max_capacity=80,
        )

        current_section = self._upsert_section(
            course=current_course,
            section_code="A1",
            faculty_user=faculty_user,
            room="LT-4",
            semester="Semester 1",
            academic_year="2026/2027",
            max_capacity=80,
            registration_opens_at=now - timedelta(days=14),
            registration_closes_at=now + timedelta(days=21),
            drop_deadline=now + timedelta(days=28),
            status=CourseSectionStatus.ACTIVE,
            timetables=[
                ("MONDAY", time(8, 0), time(10, 0)),
                ("THURSDAY", time(8, 0), time(9, 0)),
            ],
        )
        current_section_two = self._upsert_section(
            course=current_course_two,
            section_code="A1",
            faculty_user=faculty_user,
            room="Lab-2",
            semester="Semester 1",
            academic_year="2026/2027",
            max_capacity=60,
            registration_opens_at=now - timedelta(days=14),
            registration_closes_at=now + timedelta(days=21),
            drop_deadline=now + timedelta(days=28),
            status=CourseSectionStatus.ACTIVE,
            timetables=[
                ("TUESDAY", time(10, 0), time(12, 0)),
            ],
        )
        historical_section = self._upsert_section(
            course=historical_course,
            section_code="B1",
            faculty_user=faculty_user,
            room="LT-1",
            semester="Semester 2",
            academic_year="2025/2026",
            max_capacity=70,
            registration_opens_at=now - timedelta(days=240),
            registration_closes_at=now - timedelta(days=210),
            drop_deadline=now - timedelta(days=180),
            status=CourseSectionStatus.ARCHIVED,
            timetables=[
                ("WEDNESDAY", time(14, 0), time(16, 0)),
            ],
        )

        self._ensure_active_enrollment(student_one, current_section, admin_user)
        self._ensure_active_enrollment(student_two, current_section, admin_user)
        self._ensure_active_enrollment(student_one, current_section_two, admin_user)

        self._upsert_attendance(current_section, faculty_user, student_one, student_two, today)
        self._upsert_attendance(current_section_two, faculty_user, student_one, None, today)

        current_grade = record_grade(
            student=student_one,
            section=current_section,
            actor_user=faculty_user,
            numeric_score="84.00",
            special_code="",
        )
        if current_grade.grade_status != GradeStatus.OFFICIAL:
            officialise_grade(grade_record=current_grade, actor_user=admin_user)

        record_grade(
            student=student_two,
            section=current_section,
            actor_user=faculty_user,
            numeric_score="68.00",
            special_code="",
        )

        GradeRecord.objects.update_or_create(
            student=student_one,
            section=historical_section,
            defaults={
                "numeric_score": "72.00",
                "letter_grade": "B",
                "grade_points": "3.00",
                "grade_status": GradeStatus.OFFICIAL,
                "special_code": "",
                "entered_by_user": faculty_user,
                "officialised_by_user": admin_user,
                "officialised_at": now - timedelta(days=120),
            },
        )

        student_one.refresh_from_db()
        student_one.academic_standing = AcademicStanding.GOOD_STANDING
        student_one.standing_override_reason = ""
        student_one.save(update_fields=["academic_standing", "standing_override_reason", "updated_at"])

        student_two.cumulative_gpa = "1.80"
        student_two.academic_standing = AcademicStanding.ACADEMIC_WARNING
        student_two.standing_override_reason = "Demo warning status for advisor and admin workflow testing."
        student_two.save(update_fields=["cumulative_gpa", "academic_standing", "standing_override_reason", "updated_at"])

        FinancialFlag.objects.update_or_create(
            student=student_one,
            flag_type="BALANCE_HOLD",
            defaults={
                "reason": "Outstanding semester balance requiring finance office clearance.",
                "effective_date": today - timedelta(days=5),
                "cleared_date": None,
                "created_by_user": admin_user,
            },
        )

        draft_note, _ = AdvisingNote.objects.update_or_create(
            student=student_one,
            note_text="Student requested additional guidance on the final-year project and internship placement.",
            defaults={
                "created_by_user": advisor_user,
                "status": AdvisingNoteStatus.DRAFT,
                "approved_by_user": None,
                "approved_at": None,
            },
        )
        approved_note, _ = AdvisingNote.objects.update_or_create(
            student=student_one,
            note_text="Advisor reviewed the transcript and recommended prioritising the research methods course.",
            defaults={
                "created_by_user": advisor_user,
                "status": AdvisingNoteStatus.APPROVED,
                "approved_by_user": admin_user,
                "approved_at": now - timedelta(days=2),
            },
        )

        correction_request, _ = StudentCorrectionRequest.objects.update_or_create(
            student=student_one,
            justification="Surname spelling differs from the national identification record.",
            defaults={
                "requested_changes": {
                    "full_name": "Temba Mwanza",
                    "national_id": "111111/11/1",
                },
                "status": StudentCorrectionRequestStatus.PENDING,
                "review_note": "",
                "reviewed_by_user": None,
                "reviewed_at": None,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo SIS data is ready."))
        self.stdout.write("")
        self.stdout.write("Use these accounts to test the system:")
        self.stdout.write(f"  admin    : admin.demo / {password}")
        self.stdout.write(f"  advisor  : advisor.demo / {password}")
        self.stdout.write(f"  faculty  : faculty.demo / {password}")
        self.stdout.write(f"  student  : student.demo1 / {password}")
        self.stdout.write(f"  student  : student.demo2 / {password}")
        self.stdout.write("")
        self.stdout.write("Seed summary:")
        self.stdout.write(f"  Student 1 profile : {student_one.student_number} ({student_one.id})")
        self.stdout.write(f"  Student 2 profile : {student_two.student_number} ({student_two.id})")
        self.stdout.write(f"  Current section   : {current_course.course_code} / {current_section.section_code}")
        self.stdout.write(f"  Secondary section : {current_course_two.course_code} / {current_section_two.section_code}")
        self.stdout.write(f"  Historical grade  : {historical_course.course_code} / student.demo1")
        self.stdout.write(f"  Draft note ID     : {draft_note.id}")
        self.stdout.write(f"  Approved note ID  : {approved_note.id}")
        self.stdout.write(f"  Correction ID     : {correction_request.id}")

    def _upsert_user(self, *, username: str, email: str, full_name: str, primary_role: str, password: str) -> User:
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "full_name": full_name,
                "primary_role": primary_role,
            },
        )
        user.email = email
        user.full_name = full_name
        user.primary_role = primary_role
        user.must_reset_password = False
        user.is_active = True
        user.is_staff = primary_role in STAFF_ROLE_CODES
        user.set_password(password)
        user.save()
        return user

    def _upsert_student_profile(
        self,
        *,
        user: User,
        student_number: str,
        national_id: str,
        date_of_birth: date,
        gender: str,
        programme: str,
        year_of_study: int,
        academic_standing: str,
    ) -> StudentProfile:
        profile, _ = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                "student_number": student_number,
                "national_id": national_id,
                "date_of_birth": date_of_birth,
                "gender": gender,
                "programme": programme,
                "year_of_study": year_of_study,
                "academic_standing": academic_standing,
            },
        )
        profile.student_number = student_number
        profile.national_id = national_id
        profile.date_of_birth = date_of_birth
        profile.gender = gender
        profile.programme = programme
        profile.year_of_study = year_of_study
        profile.academic_standing = academic_standing
        profile.is_active = True
        profile.save()
        return profile

    def _upsert_assignment(self, student: StudentProfile, advisor_user: User, effective_from: date):
        AdvisorAssignment.objects.filter(student=student).exclude(advisor_user=advisor_user).update(
            is_current=False,
            effective_to=effective_from,
        )
        AdvisorAssignment.objects.update_or_create(
            student=student,
            advisor_user=advisor_user,
            defaults={
                "effective_from": effective_from,
                "effective_to": None,
                "is_current": True,
            },
        )

    def _upsert_course(
        self,
        *,
        course_code: str,
        course_title: str,
        department: str,
        credit_hours: int,
        description: str,
        programme_code: str,
        max_capacity: int,
    ) -> Course:
        course, _ = Course.objects.update_or_create(
            course_code=course_code,
            defaults={
                "course_title": course_title,
                "department": department,
                "credit_hours": credit_hours,
                "description": description,
                "programme_code": programme_code,
                "max_capacity": max_capacity,
                "is_active": True,
            },
        )
        return course

    def _upsert_section(
        self,
        *,
        course: Course,
        section_code: str,
        faculty_user: User,
        room: str,
        semester: str,
        academic_year: str,
        max_capacity: int,
        registration_opens_at,
        registration_closes_at,
        drop_deadline,
        status: str,
        timetables: list[tuple[str, time, time]],
    ) -> CourseSection:
        section, _ = CourseSection.objects.update_or_create(
            course=course,
            section_code=section_code,
            semester=semester,
            academic_year=academic_year,
            defaults={
                "faculty_user": faculty_user,
                "room": room,
                "max_capacity": max_capacity,
                "registration_opens_at": registration_opens_at,
                "registration_closes_at": registration_closes_at,
                "drop_deadline": drop_deadline,
                "status": status,
            },
        )
        section.timetables.all().delete()
        SectionTimetable.objects.bulk_create(
            [
                SectionTimetable(
                    section=section,
                    day_of_week=day_of_week,
                    start_time=start_time,
                    end_time=end_time,
                )
                for day_of_week, start_time, end_time in timetables
            ]
        )
        return section

    def _ensure_active_enrollment(self, student: StudentProfile, section: CourseSection, actor_user: User):
        enrollment = Enrollment.objects.filter(
            student=student,
            section=section,
            is_active=True,
            enrollment_status=EnrollmentStatus.ENROLLED,
        ).first()
        if enrollment:
            return enrollment
        return create_enrollment(
            student=student,
            section=section,
            actor_user=actor_user,
            actor_role=RoleCode.ADMIN,
            allow_waitlist=False,
        )

    def _upsert_attendance(
        self,
        section: CourseSection,
        faculty_user: User,
        student_one: StudentProfile,
        student_two: StudentProfile | None,
        today: date,
    ):
        session_dates = [today - timedelta(days=14), today - timedelta(days=7), today - timedelta(days=1)]
        for index, session_date in enumerate(session_dates, start=1):
            session, _ = AttendanceSession.objects.get_or_create(
                section=section,
                session_date=session_date,
                defaults={"recorded_by_user": faculty_user},
            )
            session.recorded_by_user = faculty_user
            session.save(update_fields=["recorded_by_user"])
            AttendanceRecord.objects.update_or_create(
                attendance_session=session,
                student=student_one,
                defaults={"status": AttendanceStatus.PRESENT},
            )
            if student_two:
                AttendanceRecord.objects.update_or_create(
                    attendance_session=session,
                    student=student_two,
                    defaults={
                        "status": AttendanceStatus.ABSENT if index == 2 else AttendanceStatus.PRESENT,
                    },
                )
