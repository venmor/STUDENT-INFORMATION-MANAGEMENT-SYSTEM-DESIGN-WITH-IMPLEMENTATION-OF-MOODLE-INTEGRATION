from rest_framework import permissions

from apps.accounts.constants import RoleCode


class IsWellbeingCoordinator(permissions.BasePermission):
    """Staff with wellbeing_coordinator capability."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_capability("wellbeing_coordinator")


class IsStudent(permissions.BasePermission):
    """Authenticated students only."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.primary_role == RoleCode.STUDENT
