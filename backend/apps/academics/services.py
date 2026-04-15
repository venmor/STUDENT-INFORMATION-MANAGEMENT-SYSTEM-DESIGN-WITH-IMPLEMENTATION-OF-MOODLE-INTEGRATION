from __future__ import annotations

import csv
import io
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from apps.integration.models import IntegrationOutboxEvent
from apps.students.models import StudentProfile

from .models import (
    AcademicStandingRule,
    AttendanceRecord,
    AttendanceStatus,
    Course,
    CourseSection,
    Enrollment,
    EnrollmentEvent,
    EnrollmentEventType,
    EnrollmentStatus,
    GradeChangeLog,
    GradeRecord,
    GradeStatus,
    GradingScaleBand,
    SpecialGradeCode,
    WaitlistEntry,
)


def create_outbox_event(event_type: str, payload: dict):
    return IntegrationOutboxEvent.objects.create(event_type=event_type, payload=payload)


def get_current_enrollment_count(section: CourseSection) -> int:
    return section.enrollments.filter(is_active=True, enrollment_status=EnrollmentStatus.ENROLLED).count()


def has_open_registration_window(section: CourseSection) -> bool:
    now = timezone.now()
    return section.registration_opens_at <= now <= section.registration_closes_at


def has_met_prerequisites(student: StudentProfile, course: Course) -> bool:
    prerequisite_ids = set(course.prerequisites.values_list("prerequisite_course_id", flat=True))
    if not prerequisite_ids:
        return True

    completed_ids = set(
        GradeRecord.objects.filter(
            student=student,
            grade_status=GradeStatus.OFFICIAL,
            section__course_id__in=prerequisite_ids,
        )
        .filter(Q(special_code="") | Q(special_code__isnull=True))
        .filter(grade_points__gt=0)
        .values_list("section__course_id", flat=True)
        .distinct()
    )
    return prerequisite_ids.issubset(completed_ids)


def select_grading_scale(score: Decimal) -> GradingScaleBand:
    for band in GradingScaleBand.objects.order_by("display_order", "-minimum_score"):
        if band.minimum_score <= score <= band.maximum_score:
            return band
    raise ValidationError("No grading scale band covers this score.")


def recalculate_student_gpa(student: StudentProfile):
    official_grades = student.grade_records.filter(grade_status=GradeStatus.OFFICIAL).select_related("section__course")
    total_quality_points = Decimal("0.00")
    total_credit_hours = Decimal("0.00")
    for record in official_grades:
        if record.special_code == SpecialGradeCode.INCOMPLETE:
            continue
        credit_hours = Decimal(record.section.course.credit_hours)
        total_quality_points += Decimal(record.grade_points) * credit_hours
        total_credit_hours += credit_hours

    if total_credit_hours == 0:
        gpa = Decimal("0.00")
    else:
        gpa = (total_quality_points / total_credit_hours).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    student.cumulative_gpa = gpa
    student.save(update_fields=["cumulative_gpa", "updated_at"])
    recalculate_academic_standing(student)
    return gpa


def recalculate_academic_standing(student: StudentProfile):
    gpa = Decimal(student.cumulative_gpa)
    selected_standing = student.academic_standing
    for rule in AcademicStandingRule.objects.order_by("display_order", "-minimum_gpa"):
        if gpa < rule.minimum_gpa:
            continue
        if rule.maximum_gpa is not None and gpa > rule.maximum_gpa:
            continue
        selected_standing = rule.standing
        break
    student.academic_standing = selected_standing
    student.save(update_fields=["academic_standing", "updated_at"])
    return selected_standing


def create_enrollment(*, student: StudentProfile, section: CourseSection, actor_user, actor_role: str, allow_waitlist: bool = False):
    existing_active = Enrollment.objects.filter(student=student, section=section, is_active=True).exists()
    if existing_active:
        raise ValidationError("Student already has an active enrollment for this section.")

    if actor_role == "STUDENT" and not has_open_registration_window(section):
        raise ValidationError("Registration window is closed for this section.")

    if not has_met_prerequisites(student, section.course):
        raise ValidationError("Student has not met this course's prerequisites.")

    current_count = get_current_enrollment_count(section)
    if current_count >= section.max_capacity:
        if not allow_waitlist:
            raise ValidationError("Section is full.")
        enrollment = Enrollment.objects.create(
            student=student,
            section=section,
            enrollment_status=EnrollmentStatus.WAITLISTED,
            actor_user=actor_user,
            actor_role=actor_role,
            is_active=True,
        )
        EnrollmentEvent.objects.create(
            enrollment=enrollment,
            event_type=EnrollmentEventType.WAITLIST,
            actor_user=actor_user,
            actor_role=actor_role,
            details={"section_id": str(section.id)},
        )
        WaitlistEntry.objects.create(student=student, section=section)
        return enrollment

    enrollment = Enrollment.objects.create(
        student=student,
        section=section,
        enrollment_status=EnrollmentStatus.ENROLLED,
        actor_user=actor_user,
        actor_role=actor_role,
        is_active=True,
    )
    EnrollmentEvent.objects.create(
        enrollment=enrollment,
        event_type=EnrollmentEventType.ENROLL,
        actor_user=actor_user,
        actor_role=actor_role,
        details={"section_id": str(section.id)},
    )
    create_outbox_event(
        "ENROLLMENT_SYNC_REQUESTED",
        {"student_id": str(student.id), "section_id": str(section.id), "action": "ENROLL"},
    )
    return enrollment


def drop_enrollment(*, enrollment: Enrollment, actor_user, actor_role: str, reason: str = ""):
    if actor_role == "STUDENT" and timezone.now() > enrollment.section.drop_deadline:
        raise ValidationError("Drop window has closed for this section.")
    enrollment.enrollment_status = EnrollmentStatus.DROPPED
    enrollment.is_active = False
    enrollment.reason = reason
    enrollment.dropped_at = timezone.now()
    enrollment.save(update_fields=["enrollment_status", "is_active", "reason", "dropped_at", "updated_at"])
    EnrollmentEvent.objects.create(
        enrollment=enrollment,
        event_type=EnrollmentEventType.DROP,
        actor_user=actor_user,
        actor_role=actor_role,
        details={"reason": reason},
    )
    create_outbox_event(
        "ENROLLMENT_SYNC_REQUESTED",
        {"student_id": str(enrollment.student_id), "section_id": str(enrollment.section_id), "action": "DROP"},
    )
    return enrollment


@transaction.atomic
def transfer_enrollment(*, enrollment: Enrollment, target_section: CourseSection, actor_user, actor_role: str):
    previous_section_id = str(enrollment.section_id)
    drop_enrollment(enrollment=enrollment, actor_user=actor_user, actor_role=actor_role, reason="Transfer")
    new_enrollment = create_enrollment(
        student=enrollment.student,
        section=target_section,
        actor_user=actor_user,
        actor_role=actor_role,
        allow_waitlist=False,
    )
    EnrollmentEvent.objects.create(
        enrollment=new_enrollment,
        event_type=EnrollmentEventType.TRANSFER,
        actor_user=actor_user,
        actor_role=actor_role,
        details={"from_section_id": previous_section_id, "to_section_id": str(target_section.id)},
    )
    return new_enrollment


def parse_bulk_enrollment_csv(uploaded_file):
    content = uploaded_file.read().decode()
    uploaded_file.seek(0)
    return list(csv.DictReader(io.StringIO(content)))


def preview_bulk_enrollment(rows):
    previews: list[dict] = []
    errors: list[dict] = []
    for index, row in enumerate(rows, start=2):
        try:
            student = StudentProfile.objects.get(pk=row["student_id"])
            section = CourseSection.objects.get(pk=row["section_id"])
            previews.append({"row_number": index, "student_id": str(student.id), "section_id": str(section.id)})
        except Exception as exc:
            errors.append({"row_number": index, "detail": str(exc)})
    return previews, errors


def commit_bulk_enrollment(rows, *, actor_user, actor_role: str):
    created: list[Enrollment] = []
    errors: list[dict] = []
    for index, row in enumerate(rows, start=2):
        try:
            student = StudentProfile.objects.get(pk=row["student_id"])
            section = CourseSection.objects.get(pk=row["section_id"])
            created.append(create_enrollment(student=student, section=section, actor_user=actor_user, actor_role=actor_role))
        except Exception as exc:
            errors.append({"row_number": index, "detail": str(exc)})
    return created, errors


def build_grade_values(*, numeric_score: Decimal | None, special_code: str):
    if special_code:
        return special_code, Decimal("0.00")
    if numeric_score is None:
        raise ValidationError("A numeric score is required when no special code is provided.")
    band = select_grading_scale(Decimal(numeric_score))
    return band.letter_grade, band.grade_points


def record_grade(*, student: StudentProfile, section: CourseSection, actor_user, numeric_score=None, special_code=""):
    letter_grade, grade_points = build_grade_values(
        numeric_score=Decimal(str(numeric_score)) if numeric_score is not None else None,
        special_code=special_code,
    )
    grade_record, _ = GradeRecord.objects.update_or_create(
        student=student,
        section=section,
        defaults={
            "numeric_score": numeric_score,
            "letter_grade": letter_grade,
            "grade_points": grade_points,
            "special_code": special_code,
            "grade_status": GradeStatus.DRAFT,
            "entered_by_user": actor_user,
        },
    )
    return grade_record


def update_grade(*, grade_record: GradeRecord, actor_user, numeric_score=None, special_code="", reason: str = ""):
    if grade_record.grade_status == GradeStatus.OFFICIAL and not reason:
        raise ValidationError("A change reason is required to update an official grade.")
    previous_numeric_score = grade_record.numeric_score
    previous_letter_grade = grade_record.letter_grade
    previous_grade_status = grade_record.grade_status
    letter_grade, grade_points = build_grade_values(
        numeric_score=Decimal(str(numeric_score)) if numeric_score is not None else None,
        special_code=special_code,
    )
    grade_record.numeric_score = numeric_score
    grade_record.special_code = special_code
    grade_record.letter_grade = letter_grade
    grade_record.grade_points = grade_points
    grade_record.save(update_fields=["numeric_score", "special_code", "letter_grade", "grade_points", "updated_at"])
    GradeChangeLog.objects.create(
        grade_record=grade_record,
        previous_numeric_score=previous_numeric_score,
        new_numeric_score=numeric_score,
        previous_letter_grade=previous_letter_grade,
        new_letter_grade=letter_grade,
        previous_grade_status=previous_grade_status,
        new_grade_status=grade_record.grade_status,
        reason=reason,
        actor_user=actor_user,
    )
    if grade_record.grade_status == GradeStatus.OFFICIAL:
        recalculate_student_gpa(grade_record.student)
    return grade_record


def officialise_grade(*, grade_record: GradeRecord, actor_user):
    grade_record.grade_status = GradeStatus.OFFICIAL
    grade_record.officialised_by_user = actor_user
    grade_record.officialised_at = timezone.now()
    grade_record.save(update_fields=["grade_status", "officialised_by_user", "officialised_at", "updated_at"])
    recalculate_student_gpa(grade_record.student)
    create_outbox_event(
        "GRADE_SYNC_REQUESTED",
        {"student_id": str(grade_record.student_id), "section_id": str(grade_record.section_id), "grade_id": str(grade_record.id)},
    )
    return grade_record


def calculate_attendance_flags(student: StudentProfile):
    flags: list[dict] = []
    active_enrollments = student.enrollments.filter(
        is_active=True,
        enrollment_status=EnrollmentStatus.ENROLLED,
    ).select_related("section__course")
    for enrollment in active_enrollments:
        records = AttendanceRecord.objects.filter(student=student, attendance_session__section=enrollment.section)
        total_count = records.count()
        if total_count == 0:
            continue
        present_count = records.filter(status__in=[AttendanceStatus.PRESENT, AttendanceStatus.EXCUSED]).count()
        percentage = (Decimal(present_count) / Decimal(total_count) * Decimal("100")).quantize(Decimal("0.01"))
        if percentage < enrollment.section.attendance_threshold:
            flags.append(
                {
                    "section_id": str(enrollment.section.id),
                    "course_code": enrollment.section.course.course_code,
                    "attendance_percentage": f"{percentage:.2f}",
                    "threshold": f"{Decimal(enrollment.section.attendance_threshold):.2f}",
                }
            )
    return flags


def generate_transcript_pdf(student: StudentProfile) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(72, 750, "Modern SIS Transcript")
    pdf.drawString(72, 732, f"Student: {student.user.full_name or student.user.username}")
    pdf.drawString(72, 714, f"Student Number: {student.student_number}")
    pdf.drawString(72, 696, f"Cumulative GPA: {student.cumulative_gpa}")
    y = 660
    for record in student.grade_records.filter(grade_status=GradeStatus.OFFICIAL).select_related("section__course").order_by("section__course__course_code"):
        pdf.drawString(72, y, f"{record.section.course.course_code} {record.section.course.course_title} - {record.letter_grade} ({record.grade_points})")
        y -= 18
        if y < 90:
            pdf.showPage()
            y = 750
    pdf.save()
    buffer.seek(0)
    return buffer.read()
