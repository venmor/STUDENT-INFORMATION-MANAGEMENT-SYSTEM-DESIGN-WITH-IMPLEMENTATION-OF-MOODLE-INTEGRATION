from __future__ import annotations

from rest_framework import serializers

from apps.academics.models import CourseSection
from apps.calendar.models import (
    AcademicCalendarAudience,
    AcademicCalendarEvent,
    AcademicCalendarEventType,
    AcademicCalendarPriority,
    AcademicCalendarSource,
    AcademicCalendarStatus,
)
from apps.calendar.services import notify_affected_users_for_event, sanitize_calendar_metadata, urgency_for_event


class AcademicCalendarEventSerializer(serializers.ModelSerializer):
    eventType = serializers.ChoiceField(source="event_type", choices=AcademicCalendarEventType.choices)
    academicYear = serializers.CharField(source="academic_year", max_length=32)
    startAt = serializers.DateTimeField(source="start_at")
    endAt = serializers.DateTimeField(source="end_at", allow_null=True, required=False)
    allDay = serializers.BooleanField(source="all_day", required=False)
    relatedCourseSection = serializers.PrimaryKeyRelatedField(
        source="related_course_section",
        queryset=CourseSection.objects.all(),
        allow_null=True,
        required=False,
        default=None,
    )
    relatedCourseSectionLabel = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    urgency = serializers.SerializerMethodField()
    metadata = serializers.JSONField(required=False)
    notifyAffectedUsers = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = AcademicCalendarEvent
        fields = (
            "id",
            "title",
            "description",
            "eventType",
            "audience",
            "priority",
            "academicYear",
            "semester",
            "startAt",
            "endAt",
            "allDay",
            "location",
            "status",
            "source",
            "relatedCourseSection",
            "relatedCourseSectionLabel",
            "urgency",
            "metadata",
            "notifyAffectedUsers",
            "createdAt",
            "updatedAt",
        )
        read_only_fields = ("id", "createdAt", "updatedAt", "urgency", "relatedCourseSectionLabel")
        extra_kwargs = {
            "audience": {"required": False, "default": AcademicCalendarAudience.ALL},
            "priority": {"required": False, "default": AcademicCalendarPriority.NORMAL},
            "status": {"required": False, "default": AcademicCalendarStatus.ACTIVE},
            "source": {"required": False, "default": AcademicCalendarSource.MANUAL},
            "description": {"required": False, "allow_blank": True},
            "location": {"required": False, "allow_blank": True},
        }

    def get_urgency(self, obj: AcademicCalendarEvent) -> str:
        return urgency_for_event(obj)

    def get_relatedCourseSectionLabel(self, obj: AcademicCalendarEvent) -> str | None:
        section = obj.related_course_section
        if section is None:
            return None
        course = getattr(section, "course", None)
        if course is None:
            return str(section.id)
        return f"{course.course_code} {section.section_code}"

    def validate_title(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Title is required.")
        return value.strip()

    def validate_academicYear(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Academic year is required.")
        return value.strip()

    def validate_semester(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("Semester is required.")
        return value.strip()

    def validate(self, attrs):
        end_at = attrs.get("end_at")
        start_at = attrs.get("start_at")
        if self.instance is not None:
            if start_at is None:
                start_at = self.instance.start_at
            if "end_at" not in attrs:
                end_at = self.instance.end_at
        if end_at is not None and start_at is not None and end_at < start_at:
            raise serializers.ValidationError({"endAt": "End date must be after the start date."})
        if "metadata" in attrs:
            attrs["metadata"] = sanitize_calendar_metadata(attrs.get("metadata"))
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["metadata"] = sanitize_calendar_metadata(instance.metadata)
        return data

    def create(self, validated_data):
        notify_affected = validated_data.pop("notifyAffectedUsers", False)
        event = super().create(validated_data)
        event.full_clean()
        if notify_affected:
            notify_affected_users_for_event(event)
        return event

    def update(self, instance, validated_data):
        notify_affected = validated_data.pop("notifyAffectedUsers", False)
        event = super().update(instance, validated_data)
        event.full_clean()
        if notify_affected:
            notify_affected_users_for_event(event)
        return event
