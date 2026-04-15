from django.contrib.auth.models import UserManager as DjangoUserManager
from django.contrib.auth.password_validation import validate_password

from .constants import RoleCode


class UserManager(DjangoUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        candidate_user = self.model(username=username, email=email, **extra_fields)
        if password is not None:
            validate_password(password, candidate_user)
        return super().create_user(username, email=email, password=password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("primary_role", RoleCode.ADMIN)
        return super().create_superuser(username, email=email, password=password, **extra_fields)
