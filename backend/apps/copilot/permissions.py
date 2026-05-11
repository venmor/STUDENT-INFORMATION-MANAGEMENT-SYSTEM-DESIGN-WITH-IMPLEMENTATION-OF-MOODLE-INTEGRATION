from __future__ import annotations

from rest_framework.exceptions import PermissionDenied

from apps.accounts.constants import RoleCode
from apps.students.models import StudentProfile

from .models import CopilotMessage, CopilotMessageRole, CopilotSession


def require_student_user(user) -> StudentProfile:
    if getattr(user, "primary_role", None) != RoleCode.STUDENT:
        raise PermissionDenied("Student access is required for the co-pilot.")
    student = getattr(user, "student_profile", None)
    if student is None:
        raise PermissionDenied("A linked student profile is required for the co-pilot.")
    return student


def owns_session(user, session: CopilotSession) -> bool:
    return session.user_id == getattr(user, "id", None)


def owns_assistant_message(user, message: CopilotMessage) -> bool:
    return message.role == CopilotMessageRole.ASSISTANT and message.session.user_id == getattr(user, "id", None)
