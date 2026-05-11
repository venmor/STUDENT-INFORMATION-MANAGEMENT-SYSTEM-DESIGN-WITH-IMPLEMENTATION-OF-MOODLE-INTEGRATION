from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.db import models

from .constants import AccessEventType, CapabilityName, RoleCode
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
    full_name = models.CharField(max_length=255, blank=True)
    primary_role = models.CharField(
        max_length=32,
        choices=RoleCode.choices,
        default=RoleCode.STUDENT,
    )
    secondary_roles = models.JSONField(default=list, blank=True)
    must_reset_password = models.BooleanField(default=False)

    objects = UserManager()

    def set_password(self, raw_password):
        if raw_password is not None:
            validate_password(raw_password, self)
        super().set_password(raw_password)

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


class AccessLog(models.Model):
    actor_user = models.ForeignKey(
        "accounts.User",
        related_name="actor_access_logs",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    subject_user = models.ForeignKey(
        "accounts.User",
        related_name="subject_access_logs",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    event_type = models.CharField(max_length=32, choices=AccessEventType.choices)
    view_name = models.CharField(max_length=128, blank=True)
    request_path = models.CharField(max_length=255, blank=True)
    request_method = models.CharField(max_length=16, blank=True)
    response_status = models.PositiveSmallIntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.event_type}:{self.request_path}:{self.response_status}"
