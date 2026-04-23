from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import AccessLog, Role, User, UserCapability


class UserCapabilityInline(admin.TabularInline):
    model = UserCapability
    extra = 0


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = [UserCapabilityInline]
    list_display = ("username", "full_name", "email", "primary_role", "is_active", "is_staff")
    list_filter = (*DjangoUserAdmin.list_filter, "primary_role")
    fieldsets = (
        *DjangoUserAdmin.fieldsets,
        ("Profile", {"fields": ("full_name",)}),
        ("Authorization", {"fields": ("primary_role", "must_reset_password")}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_staff_role")
    search_fields = ("code", "name")


@admin.register(UserCapability)
class UserCapabilityAdmin(admin.ModelAdmin):
    list_display = ("user", "capability_name", "granted_at")
    list_filter = ("capability_name", "granted_at")
    search_fields = ("user__username", "user__email")


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ("event_type", "actor_user", "subject_user", "request_path", "response_status", "created_at")
    list_filter = ("event_type", "response_status", "created_at")
    search_fields = (
        "actor_user__username",
        "subject_user__username",
        "request_path",
        "view_name",
    )
