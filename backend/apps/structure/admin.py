from django.contrib import admin

from apps.structure.models import Department, Programme, School, Stream


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_active"]
    search_fields = ["code", "name"]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "school", "is_active"]
    list_filter = ["school"]
    search_fields = ["code", "name"]


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "department", "level", "duration_years", "is_active"]
    list_filter = ["level", "department"]
    search_fields = ["code", "name"]


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "programme", "is_active"]
    list_filter = ["programme"]
    search_fields = ["code", "name"]
