from django.contrib import admin

from .models import AcademicCalendarEvent


@admin.register(AcademicCalendarEvent)
class AcademicCalendarEventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "audience", "priority", "status", "academic_year", "semester", "start_at", "source")
    list_filter = ("event_type", "audience", "priority", "status", "source", "academic_year", "semester")
    search_fields = ("title", "description", "academic_year", "semester")
    readonly_fields = ("created_at", "updated_at")
