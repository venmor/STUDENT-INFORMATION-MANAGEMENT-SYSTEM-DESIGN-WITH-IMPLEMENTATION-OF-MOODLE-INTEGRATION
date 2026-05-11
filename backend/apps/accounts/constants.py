from django.db import models


class RoleCode(models.TextChoices):
    STUDENT = "STUDENT", "Student"
    ADVISOR = "ADVISOR", "Advisor"
    FACULTY = "FACULTY", "Faculty"
    ADMIN = "ADMIN", "Admin"


class CapabilityName(models.TextChoices):
    WELLBEING_COORDINATOR = "wellbeing_coordinator", "Wellbeing coordinator"


STAFF_ROLE_CODES = {
    RoleCode.ADVISOR,
    RoleCode.FACULTY,
    RoleCode.ADMIN,
}
