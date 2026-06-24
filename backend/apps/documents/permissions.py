from __future__ import annotations

from apps.accounts.constants import RoleCode
from apps.documents.models import DocumentVisibility, StudentDocument
from apps.students.models import StudentProfile


def is_admin(user) -> bool:
    return getattr(user, "primary_role", None) == RoleCode.ADMIN


def is_student_owner(user, student: StudentProfile) -> bool:
    return getattr(user, "primary_role", None) == RoleCode.STUDENT and student.user_id == getattr(user, "id", None)


def is_assigned_advisor(user, student: StudentProfile) -> bool:
    if getattr(user, "primary_role", None) != RoleCode.ADVISOR:
        return False
    return student.advisor_assignments.filter(advisor_user=user, is_current=True).exists()


def can_view_student_documents(user, student: StudentProfile) -> bool:
    return is_admin(user) or is_student_owner(user, student) or is_assigned_advisor(user, student)


def can_upload_document_for_student(user, student: StudentProfile) -> bool:
    return is_admin(user) or is_student_owner(user, student)


def can_view_document(user, document: StudentDocument) -> bool:
    # Visibility is deliberately narrower than "can view student": advisors see
    # only advisor/student-visible records, while students see only documents
    # explicitly released to them.
    if is_admin(user):
        return True
    if is_student_owner(user, document.student):
        return document.visibility == DocumentVisibility.STUDENT_VISIBLE
    if is_assigned_advisor(user, document.student):
        return document.visibility in {
            DocumentVisibility.ADMIN_ADVISOR,
            DocumentVisibility.STUDENT_VISIBLE,
        }
    return False


def can_download_document(user, document: StudentDocument) -> bool:
    return can_view_document(user, document)


def can_review_document(user, document: StudentDocument) -> bool:
    return is_admin(user)


def can_archive_document(user, document: StudentDocument) -> bool:
    return is_admin(user)


def can_update_document(user, document: StudentDocument) -> bool:
    return is_admin(user)
