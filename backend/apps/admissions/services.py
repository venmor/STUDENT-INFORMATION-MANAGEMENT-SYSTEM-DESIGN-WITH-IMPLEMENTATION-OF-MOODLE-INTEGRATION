import io
import uuid
from datetime import date

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.accounts.models import User
from apps.admissions.models import ApplicantProfile, ApplicationStatus
from apps.documents.models import StudentDocument
from apps.notifications.services import create_notification
from apps.students.models import StudentProfile


def approve_application(applicant: ApplicantProfile, reviewed_by: User) -> User:
    username = f"{applicant.full_name.lower().replace(' ', '.')}.{str(applicant.id)[:4]}"
    temp_password = f"Welcome{uuid.uuid4().hex[:8]}!"

    new_user = User.objects.create_user(
        username=username,
        email=applicant.email,
        password=temp_password,
        full_name=applicant.full_name,
        primary_role="STUDENT",
        must_reset_password=True,
    )

    StudentProfile.objects.create(
        user=new_user,
        student_number=f"STU-{str(applicant.id)[:8].upper()}",
        date_of_birth=applicant.date_of_birth,
        gender=applicant.gender,
        programme=applicant.programme_applied.name if applicant.programme_applied else "Unassigned",
        programme_ref=applicant.programme_applied,
        year_of_study=1,
    )

    applicant.application_status = ApplicationStatus.ACCEPTED
    applicant.reviewed_by = reviewed_by
    applicant.reviewed_at = timezone.now()
    applicant.converted_user = new_user
    applicant.save()

    pdf_content = _generate_acceptance_letter(applicant, username, temp_password)
    doc = StudentDocument(
        student=StudentProfile.objects.get(user=new_user),
        title="Admission Letter",
        document_type="ADMISSION_LETTER",
        uploaded_by=reviewed_by,
    )
    from django.core.files.base import ContentFile
    doc.file.save(f"admission_letter_{applicant.id}.pdf", ContentFile(pdf_content))
    doc.save()

    create_notification(
        recipient=new_user,
        category="ACADEMIC",
        severity="SUCCESS",
        title="Welcome! Your application has been accepted",
        message=f"Your account has been created. Username: {username}. Please change your password on first login.",
    )

    return new_user


def reject_application(applicant: ApplicantProfile, reviewed_by: User, notes: str = "") -> None:
    applicant.application_status = ApplicationStatus.REJECTED
    applicant.reviewed_by = reviewed_by
    applicant.reviewed_at = timezone.now()
    applicant.review_notes = notes
    applicant.save()


def _generate_acceptance_letter(applicant: ApplicantProfile, username: str, temp_password: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("STUDENT INFORMATION SYSTEM", styles["Title"]))
    elements.append(Spacer(1, 24))
    elements.append(Paragraph("ADMISSION ACCEPTANCE LETTER", styles["Heading2"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Date: {date.today().isoformat()}", styles["Normal"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Dear {applicant.full_name},", styles["Normal"]))
    elements.append(Spacer(1, 8))

    programme_name = applicant.programme_applied.name if applicant.programme_applied else "the programme"
    elements.append(Paragraph(
        f"Congratulations! We are pleased to inform you that your application to {programme_name} "
        f"has been accepted. Your student account has been created with the following credentials:",
        styles["Normal"],
    ))
    elements.append(Spacer(1, 12))

    data = [
        ["Username", username],
        ["Temporary Password", temp_password],
    ]
    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        "Please log in and change your password immediately. We look forward to welcoming you.",
        styles["Normal"],
    ))

    doc.build(elements)
    return buffer.getvalue()
