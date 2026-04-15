from __future__ import annotations

from rest_framework import serializers

from apps.academics.models import Course, CoursePrerequisite, CourseSection, Enrollment, GradeRecord, SectionTimetable


class SectionTimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionTimetable
        fields = ("id", "day_of_week", "start_time", "end_time")
        read_only_fields = ("id",)


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "course_code",
            "course_title",
            "department",
            "credit_hours",
            "description",
            "programme_code",
            "max_capacity",
            "is_active",
        )


class CourseSectionSerializer(serializers.ModelSerializer):
    course_id = serializers.UUIDField()
    faculty_user_id = serializers.IntegerField()
    timetables = SectionTimetableSerializer(many=True)
    current_enrollment_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseSection
        fields = (
            "id",
            "course_id",
            "section_code",
            "faculty_user_id",
            "room",
            "semester",
            "academic_year",
            "max_capacity",
            "registration_opens_at",
            "registration_closes_at",
            "drop_deadline",
            "attendance_threshold",
            "status",
            "timetables",
            "current_enrollment_count",
        )

    def create(self, validated_data):
        timetables_data = validated_data.pop("timetables", [])
        section = CourseSection.objects.create(**validated_data)
        for timetable in timetables_data:
            SectionTimetable.objects.create(section=section, **timetable)
        return section

    def update(self, instance, validated_data):
        timetables_data = validated_data.pop("timetables", None)
        instance = super().update(instance, validated_data)
        if timetables_data is not None:
            instance.timetables.all().delete()
            for timetable in timetables_data:
                SectionTimetable.objects.create(section=instance, **timetable)
        return instance

    def get_current_enrollment_count(self, obj):
        from apps.academics.services import get_current_enrollment_count

        return get_current_enrollment_count(obj)


class PrerequisiteCreateSerializer(serializers.ModelSerializer):
    prerequisite_course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source="prerequisite_course",
    )

    class Meta:
        model = CoursePrerequisite
        fields = ("prerequisite_course_id",)


class EnrollmentSerializer(serializers.ModelSerializer):
    student_id = serializers.UUIDField(read_only=True)
    section_id = serializers.UUIDField(read_only=True)
    section = CourseSectionSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = (
            "id",
            "student_id",
            "section_id",
            "enrollment_status",
            "is_active",
            "reason",
            "enrolled_at",
            "dropped_at",
            "section",
        )
        read_only_fields = ("id", "enrollment_status", "is_active", "reason", "enrolled_at", "dropped_at", "section")


class EnrollmentCreateSerializer(serializers.Serializer):
    section_id = serializers.UUIDField()
    student_user_id = serializers.IntegerField(required=False)
    waitlist_if_full = serializers.BooleanField(default=False)


class EnrollmentTransferSerializer(serializers.Serializer):
    target_section_id = serializers.UUIDField()


class BulkEnrollmentFileSerializer(serializers.Serializer):
    file = serializers.FileField()


class GradeRecordSerializer(serializers.ModelSerializer):
    student_id = serializers.UUIDField(read_only=True)
    section_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = GradeRecord
        fields = ("id", "student_id", "section_id", "numeric_score", "letter_grade", "grade_points", "grade_status", "special_code")
        read_only_fields = ("id", "letter_grade", "grade_points", "grade_status")


class GradeCreateSerializer(serializers.Serializer):
    student_user_id = serializers.IntegerField()
    section_id = serializers.UUIDField()
    numeric_score = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    special_code = serializers.CharField(required=False, allow_blank=True)


class GradeUpdateSerializer(serializers.Serializer):
    numeric_score = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    special_code = serializers.CharField(required=False, allow_blank=True)
    change_reason = serializers.CharField(required=False, allow_blank=True)


class AttendanceRecordInputSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    status = serializers.CharField()


class AttendanceSessionCreateSerializer(serializers.Serializer):
    section_id = serializers.UUIDField()
    session_date = serializers.DateField()
    records = AttendanceRecordInputSerializer(many=True)
