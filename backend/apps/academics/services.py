from __future__ import annotations

import csv
import io
import logging
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

logger = logging.getLogger(__name__)


def create_outbox_event(event_type: str, payload: dict):
    from apps.integration.services import create_sync_event

    return create_sync_event(event_type=event_type, payload=payload)


def notify_enrollment_confirmed(enrollment: Enrollment) -> None:
    try:
        from apps.notifications.models import NotificationCategory, NotificationSeverity
        from apps.notifications.services import create_notification

        section = enrollment.section
        create_notification(
            recipient=enrollment.student.user,
            category=NotificationCategory.ENROLLMENT,
            severity=NotificationSeverity.SUCCESS,
            title="Enrollment confirmed",
            message=f"Your enrollment in {section.course.course_code} {section.section_code} is confirmed.",
            action_label="View courses",
            action_url="/student/courses",
            source_type="Enrollment",
            source_id=str(enrollment.id),
            metadata={
                "section_id": str(section.id),
                "course_code": section.course.course_code,
                "enrollment_status": enrollment.enrollment_status,
            },
        )
    except Exception:
        logger.exception("Failed to create enrollment notification for enrollment %s", enrollment.id)


def notify_grade_released(grade_record: GradeRecord) -> None:
    try:
        from apps.notifications.models import NotificationCategory, NotificationSeverity
        from apps.notifications.services import create_notification

        section = grade_record.section
        create_notification(
            recipient=grade_record.student.user,
            category=NotificationCategory.GRADES,
            severity=NotificationSeverity.SUCCESS,
            title="Grade released",
            message=f"Your official grade for {section.course.course_code} {section.section_code} is available.",
            action_label="View grades",
            action_url="/student/grades",
            source_type="GradeRecord",
            source_id=str(grade_record.id),
            metadata={
                "section_id": str(section.id),
                "course_code": section.course.course_code,
                "grade_status": grade_record.grade_status,
            },
        )
    except Exception:
        logger.exception("Failed to create grade notification for grade record %s", grade_record.id)


def record_academic_audit(
    *,
    actor_user,
    category: str,
    action: str,
    summary: str,
    target_type: str,
    target_id: str,
    severity: str = "INFO",
    metadata: dict | None = None,
) -> None:
    try:
        from apps.audit.services import record_audit_event_safely

        record_audit_event_safely(
            actor=actor_user,
            category=category,
            action=action,
            summary=summary,
            target_type=target_type,
            target_id=target_id,
            severity=severity,
            metadata=metadata or {},
        )
    except Exception:
        logger.exception("Failed to record academic audit event %s for %s %s", action, target_type, target_id)


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
        record_academic_audit(
            actor_user=actor_user,
            category="ENROLLMENT",
            action="ENROLLMENT_CREATED",
            summary=f"Enrollment record created for {student.student_number} in {section.course.course_code} {section.section_code}.",
            target_type="Enrollment",
            target_id=str(enrollment.id),
            severity="INFO",
            metadata={
                "studentId": str(student.id),
                "sectionId": str(section.id),
                "status": enrollment.enrollment_status,
                "courseCode": section.course.course_code,
            },
        )
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
        {"enrollment_id": str(enrollment.id), "student_id": str(student.id), "section_id": str(section.id), "action": "ENROLL"},
    )
    notify_enrollment_confirmed(enrollment)
    record_academic_audit(
        actor_user=actor_user,
        category="ENROLLMENT",
        action="ENROLLMENT_CREATED",
        summary=f"Enrollment record created for {student.student_number} in {section.course.course_code} {section.section_code}.",
        target_type="Enrollment",
        target_id=str(enrollment.id),
        severity="SUCCESS",
        metadata={
            "studentId": str(student.id),
            "sectionId": str(section.id),
            "status": enrollment.enrollment_status,
            "courseCode": section.course.course_code,
        },
    )
    return enrollment


def create_enrollment_pending(*, student: StudentProfile, section: CourseSection, actor_user, actor_role: str):
    existing_active = Enrollment.objects.filter(student=student, section=section, is_active=True).exists()
    if existing_active:
        raise ValidationError("Student already has an active enrollment for this section.")

    if not has_met_prerequisites(student, section.course):
        raise ValidationError("Student has not met this course's prerequisites.")

    enrollment = Enrollment.objects.create(
        student=student,
        section=section,
        enrollment_status=EnrollmentStatus.PENDING_APPROVAL,
        actor_user=actor_user,
        actor_role=actor_role,
        is_active=True,
        approval_required=True,
    )
    EnrollmentEvent.objects.create(
        enrollment=enrollment,
        event_type=EnrollmentEventType.PENDING_APPROVAL,
        actor_user=actor_user,
        actor_role=actor_role,
        details={"section_id": str(section.id)},
    )
    record_academic_audit(
        actor_user=actor_user,
        category="ENROLLMENT",
        action="ENROLLMENT_PENDING_APPROVAL",
        summary=f"Enrollment pending approval for {student.student_number} in {section.course.course_code} {section.section_code}.",
        target_type="Enrollment",
        target_id=str(enrollment.id),
        severity="INFO",
        metadata={
            "studentId": str(student.id),
            "sectionId": str(section.id),
            "status": enrollment.enrollment_status,
            "courseCode": section.course.course_code,
        },
    )
    return enrollment


def approve_enrollment(*, enrollment: Enrollment, actor_user):
    if enrollment.enrollment_status != EnrollmentStatus.PENDING_APPROVAL:
        raise ValidationError("Only pending-approval enrollments can be approved.")

    current_count = get_current_enrollment_count(enrollment.section)
    if current_count >= enrollment.section.max_capacity:
        raise ValidationError("Section is full. Cannot approve enrollment.")

    enrollment.enrollment_status = EnrollmentStatus.ENROLLED
    enrollment.approved_by = actor_user
    enrollment.approved_at = timezone.now()
    enrollment.save(update_fields=["enrollment_status", "approved_by", "approved_at", "updated_at"])
    EnrollmentEvent.objects.create(
        enrollment=enrollment,
        event_type=EnrollmentEventType.APPROVED,
        actor_user=actor_user,
        actor_role="ADVISOR",
        details={"section_id": str(enrollment.section_id)},
    )
    create_outbox_event(
        "ENROLLMENT_SYNC_REQUESTED",
        {"enrollment_id": str(enrollment.id), "student_id": str(enrollment.student_id), "section_id": str(enrollment.section_id), "action": "ENROLL"},
    )
    notify_enrollment_confirmed(enrollment)
    record_academic_audit(
        actor_user=actor_user,
        category="ENROLLMENT",
        action="ENROLLMENT_APPROVED",
        summary=f"Enrollment approved for {enrollment.student.student_number} in {enrollment.section.course.course_code} {enrollment.section.section_code}.",
        target_type="Enrollment",
        target_id=str(enrollment.id),
        severity="SUCCESS",
        metadata={
            "studentId": str(enrollment.student_id),
            "sectionId": str(enrollment.section_id),
            "courseCode": enrollment.section.course.course_code,
        },
    )
    return enrollment


def reject_enrollment(*, enrollment: Enrollment, actor_user, reason: str = ""):
    if enrollment.enrollment_status != EnrollmentStatus.PENDING_APPROVAL:
        raise ValidationError("Only pending-approval enrollments can be rejected.")

    enrollment.enrollment_status = EnrollmentStatus.DROPPED
    enrollment.is_active = False
    enrollment.rejection_reason = reason
    enrollment.save(update_fields=["enrollment_status", "is_active", "rejection_reason", "updated_at"])
    EnrollmentEvent.objects.create(
        enrollment=enrollment,
        event_type=EnrollmentEventType.REJECTED,
        actor_user=actor_user,
        actor_role="ADVISOR",
        details={"reason": reason},
    )
    record_academic_audit(
        actor_user=actor_user,
        category="ENROLLMENT",
        action="ENROLLMENT_REJECTED",
        summary=f"Enrollment rejected for {enrollment.student.student_number} in {enrollment.section.course.course_code} {enrollment.section.section_code}.",
        target_type="Enrollment",
        target_id=str(enrollment.id),
        severity="WARNING",
        metadata={
            "studentId": str(enrollment.student_id),
            "sectionId": str(enrollment.section_id),
            "reason": reason,
            "courseCode": enrollment.section.course.course_code,
        },
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
        {
            "enrollment_id": str(enrollment.id),
            "student_id": str(enrollment.student_id),
            "section_id": str(enrollment.section_id),
            "action": "DROP",
        },
    )
    record_academic_audit(
        actor_user=actor_user,
        category="ENROLLMENT",
        action="ENROLLMENT_DROPPED",
        summary=f"Enrollment record dropped for {enrollment.student.student_number} in {enrollment.section.course.course_code} {enrollment.section.section_code}.",
        target_type="Enrollment",
        target_id=str(enrollment.id),
        severity="WARNING",
        metadata={
            "studentId": str(enrollment.student_id),
            "sectionId": str(enrollment.section_id),
            "reason": reason,
            "courseCode": enrollment.section.course.course_code,
        },
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


def validate_active_enrollment(student: StudentProfile, section: CourseSection):
    has_active_enrollment = Enrollment.objects.filter(
        student=student,
        section=section,
        is_active=True,
        enrollment_status=EnrollmentStatus.ENROLLED,
    ).exists()
    if not has_active_enrollment:
        raise ValidationError("Student must have an active enrollment in this section.")


def record_grade(*, student: StudentProfile, section: CourseSection, actor_user, numeric_score=None, ca_score=None, exam_score=None, special_code=""):
    validate_active_enrollment(student, section)
    if numeric_score is None and ca_score is not None and exam_score is not None and not special_code:
        numeric_score = Decimal(str(ca_score)) + Decimal(str(exam_score))
    letter_grade, grade_points = build_grade_values(
        numeric_score=Decimal(str(numeric_score)) if numeric_score is not None else None,
        special_code=special_code,
    )
    grade_record, _ = GradeRecord.objects.update_or_create(
        student=student,
        section=section,
        defaults={
            "ca_score": ca_score,
            "exam_score": exam_score,
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
    validate_active_enrollment(grade_record.student, grade_record.section)
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
    validate_active_enrollment(grade_record.student, grade_record.section)
    grade_record.grade_status = GradeStatus.OFFICIAL
    grade_record.officialised_by_user = actor_user
    grade_record.officialised_at = timezone.now()
    grade_record.save(update_fields=["grade_status", "officialised_by_user", "officialised_at", "updated_at"])
    recalculate_student_gpa(grade_record.student)
    create_outbox_event(
        "GRADE_SYNC_REQUESTED",
        {"student_id": str(grade_record.student_id), "section_id": str(grade_record.section_id), "grade_id": str(grade_record.id)},
    )
    notify_grade_released(grade_record)
    record_academic_audit(
        actor_user=actor_user,
        category="GRADE",
        action="GRADE_OFFICIALISED",
        summary=f"Official grade released for {grade_record.student.student_number} in {grade_record.section.course.course_code} {grade_record.section.section_code}.",
        target_type="GradeRecord",
        target_id=str(grade_record.id),
        severity="SUCCESS",
        metadata={
            "studentId": str(grade_record.student_id),
            "sectionId": str(grade_record.section_id),
            "courseCode": grade_record.section.course.course_code,
            "gradeStatus": grade_record.grade_status,
        },
    )
    return grade_record


def calculate_attendance_percentages(student: StudentProfile):
    percentages: list[dict] = []
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
        percentages.append(
            {
                "section_id": str(enrollment.section.id),
                "course_code": enrollment.section.course.course_code,
                "attendance_percentage": f"{percentage:.2f}",
                "threshold": f"{Decimal(enrollment.section.attendance_threshold):.2f}",
            }
        )
    return percentages


def calculate_attendance_flags(student: StudentProfile):
    return [
        percentage
        for percentage in calculate_attendance_percentages(student)
        if Decimal(percentage["attendance_percentage"]) < Decimal(percentage["threshold"])
    ]


class AcademicOutcome:
    CLEAR = "CLEAR"
    SUPPLEMENTARY = "SUPPLEMENTARY"
    REPEAT = "REPEAT"


def determine_academic_outcome(student: StudentProfile, semester: str, academic_year: str) -> str:
    grades = student.grade_records.filter(
        grade_status=GradeStatus.OFFICIAL,
        section__semester=semester,
        section__academic_year=academic_year,
    ).select_related("section__course")

    if not grades.exists():
        return AcademicOutcome.CLEAR

    failing_grades = []
    for record in grades:
        if record.special_code == SpecialGradeCode.INCOMPLETE:
            failing_grades.append(record)
            continue
        band = None
        try:
            band = GradingScaleBand.objects.filter(
                minimum_score__lte=record.numeric_score,
                maximum_score__gte=record.numeric_score,
            ).first()
        except (TypeError, ValueError):
            pass
        if band and not band.is_passing:
            failing_grades.append(record)

    if not failing_grades:
        return AcademicOutcome.CLEAR

    total_failing_credits = sum(r.section.course.credit_hours for r in failing_grades)
    total_credits = sum(r.section.course.credit_hours for r in grades)

    if total_credits > 0 and total_failing_credits / total_credits > Decimal("0.5"):
        return AcademicOutcome.REPEAT

    return AcademicOutcome.SUPPLEMENTARY


def generate_exam_slip_pdf(student: StudentProfile, semester: str, academic_year: str) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(72, 750, "EXAMINATION PERMIT")
    pdf.drawString(72, 730, f"Student: {student.user.full_name or student.user.username}")
    pdf.drawString(72, 712, f"Student Number: {student.student_number}")
    pdf.drawString(72, 694, f"Semester: {semester} | Academic Year: {academic_year}")
    y = 660
    enrollments = student.enrollments.filter(
        is_active=True,
        enrollment_status=EnrollmentStatus.ENROLLED,
        section__semester=semester,
        section__academic_year=academic_year,
    ).select_related("section__course")
    for enrollment in enrollments:
        course = enrollment.section.course
        pdf.drawString(72, y, f"{course.course_code} - {course.course_title} ({course.credit_hours} cr)")
        y -= 18
        if y < 90:
            pdf.showPage()
            y = 750
    pdf.save()
    buffer.seek(0)
    return buffer.read()


def generate_results_slip_pdf(student: StudentProfile, semester: str, academic_year: str) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(72, 750, "RESULTS SLIP")
    pdf.drawString(72, 730, f"Student: {student.user.full_name or student.user.username}")
    pdf.drawString(72, 712, f"Student Number: {student.student_number}")
    pdf.drawString(72, 694, f"Semester: {semester} | Academic Year: {academic_year}")
    y = 660
    grades = student.grade_records.filter(
        grade_status=GradeStatus.OFFICIAL,
        section__semester=semester,
        section__academic_year=academic_year,
    ).select_related("section__course")
    for record in grades:
        course = record.section.course
        line = f"{course.course_code} - {course.course_title}: {record.letter_grade} ({record.grade_points})"
        pdf.drawString(72, y, line)
        y -= 18
        if y < 90:
            pdf.showPage()
            y = 750
    outcome = determine_academic_outcome(student, semester, academic_year)
    pdf.drawString(72, y - 20, f"Outcome: {outcome}")
    pdf.save()
    buffer.seek(0)
    return buffer.read()


def generate_grade_template_csv(section: CourseSection) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["student_id", "student_number", "student_name", "ca_score", "exam_score"])
    enrollments = section.enrollments.filter(
        is_active=True,
        enrollment_status=EnrollmentStatus.ENROLLED,
    ).select_related("student__user").order_by("student__student_number")
    for enrollment in enrollments:
        writer.writerow([
            str(enrollment.student_id),
            enrollment.student.student_number,
            enrollment.student.user.full_name or enrollment.student.user.username,
            "",
            "",
        ])
    return output.getvalue()


def parse_grade_upload_csv(uploaded_file) -> list[dict]:
    content = uploaded_file.read().decode()
    uploaded_file.seek(0)
    return list(csv.DictReader(io.StringIO(content)))


def preview_grade_upload(rows: list[dict], section: CourseSection):
    previews: list[dict] = []
    errors: list[dict] = []
    for index, row in enumerate(rows, start=2):
        try:
            student = StudentProfile.objects.get(pk=row["student_id"])
            ca = Decimal(row["ca_score"]) if row.get("ca_score") else None
            exam = Decimal(row["exam_score"]) if row.get("exam_score") else None
            total = (ca or Decimal("0")) + (exam or Decimal("0")) if (ca is not None or exam is not None) else None
            previews.append({
                "row_number": index,
                "student_id": str(student.id),
                "student_number": student.student_number,
                "ca_score": str(ca) if ca else None,
                "exam_score": str(exam) if exam else None,
                "total": str(total) if total else None,
            })
        except Exception as exc:
            errors.append({"row_number": index, "detail": str(exc)})
    return previews, errors


def commit_grade_upload(rows: list[dict], section: CourseSection, *, actor_user):
    created: list[GradeRecord] = []
    errors: list[dict] = []
    for index, row in enumerate(rows, start=2):
        try:
            student = StudentProfile.objects.get(pk=row["student_id"])
            ca = Decimal(row["ca_score"]) if row.get("ca_score") else None
            exam = Decimal(row["exam_score"]) if row.get("exam_score") else None
            grade = record_grade(
                student=student,
                section=section,
                actor_user=actor_user,
                ca_score=ca,
                exam_score=exam,
            )
            created.append(grade)
        except Exception as exc:
            errors.append({"row_number": index, "detail": str(exc)})
    return created, errors


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
