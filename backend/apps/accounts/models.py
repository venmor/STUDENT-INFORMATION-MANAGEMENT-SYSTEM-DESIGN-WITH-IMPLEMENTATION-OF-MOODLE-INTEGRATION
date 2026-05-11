from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import CapabilityName, RoleCode
from .managers import UserManager


class Role(models.Model):
    code = models.CharField(max_length=32, primary_key=True, choices=RoleCode.choices)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True)
    is_staff_role = models.BooleanField(default=False)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    primary_role = models.CharField(
        max_length=32,
        choices=RoleCode.choices,
        default=RoleCode.STUDENT,
    )

    objects = UserManager()

    def has_role(self, role_code: str) -> bool:
        return self.primary_role == role_code

    def has_capability(self, capability_name: str) -> bool:
        return self.capabilities.filter(capability_name=capability_name).exists()


class UserCapability(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        related_name="capabilities",
        on_delete=models.CASCADE,
    )
    capability_name = models.CharField(max_length=64, choices=CapabilityName.choices)
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "capability_name"],
                name="accounts_user_capability_unique",
            )
        ]
        ordering = ["capability_name"]

    def __str__(self) -> str:
        return f"{self.user.username}:{self.capability_name}"

