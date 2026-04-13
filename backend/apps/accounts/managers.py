from django.contrib.auth.models import UserManager as DjangoUserManager

from .constants import RoleCode


class UserManager(DjangoUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("primary_role", RoleCode.ADMIN)
        return super().create_superuser(username, email=email, password=password, **extra_fields)

