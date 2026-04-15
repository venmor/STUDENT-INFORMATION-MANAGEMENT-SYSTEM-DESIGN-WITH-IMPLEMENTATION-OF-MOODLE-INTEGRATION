from django.db import models


class RoleCode(models.TextChoices):
    STUDENT = "STUDENT", "Student"
    ADVISOR = "ADVISOR", "Advisor"
    FACULTY = "FACULTY", "Faculty"
    ADMIN = "ADMIN", "Admin"


class CapabilityName(models.TextChoices):
    WELLBEING_COORDINATOR = "wellbeing_coordinator", "Wellbeing coordinator"


class AccessEventType(models.TextChoices):
    LOGIN_SUCCESS = "LOGIN_SUCCESS", "Login success"
    LOGIN_FAILURE = "LOGIN_FAILURE", "Login failure"
    PASSWORD_CHANGE = "PASSWORD_CHANGE", "Password change"
    PASSWORD_RESET = "PASSWORD_RESET", "Password reset"
    USER_CREATED = "USER_CREATED", "User created"
    USER_UPDATED = "USER_UPDATED", "User updated"
    USER_DEACTIVATED = "USER_DEACTIVATED", "User deactivated"
    API_ACTION = "API_ACTION", "API action"


STAFF_ROLE_CODES = {
    RoleCode.ADVISOR,
    RoleCode.FACULTY,
    RoleCode.ADMIN,
}
