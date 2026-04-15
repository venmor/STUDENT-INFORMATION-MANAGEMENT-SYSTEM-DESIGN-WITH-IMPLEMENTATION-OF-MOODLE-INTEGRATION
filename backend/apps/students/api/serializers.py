from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import User
from apps.students.models import AdvisorAssignment, AdvisingNote, FinancialFlag, StudentProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    attendance_flags = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = (
            "id",
            "user_id",
            "username",
            "full_name",
            "email",
            "student_number",
            "national_id",
            "date_of_birth",
            "gender",
            "programme",
            "year_of_study",
            "academic_standing",
            "cumulative_gpa",
            "standing_override_reason",
            "is_active",
            "attendance_flags",
        )
        read_only_fields = ("cumulative_gpa", "attendance_flags")

    def get_attendance_flags(self, obj):
        from apps.academics.services import calculate_attendance_flags

        return calculate_attendance_flags(obj)


class StudentProfileCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="user")
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = StudentProfile
        fields = (
            "id",
            "user_id",
            "student_number",
            "national_id",
            "date_of_birth",
            "gender",
            "programme",
            "year_of_study",
        )


class AdvisorAssignmentSerializer(serializers.ModelSerializer):
    advisor_user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="advisor_user")

    class Meta:
        model = AdvisorAssignment
        fields = ("id", "advisor_user_id", "effective_from", "effective_to", "is_current")


class FinancialFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialFlag
        fields = ("id", "flag_type", "reason", "effective_date", "cleared_date", "created_at")
        read_only_fields = ("id", "created_at")


class AdvisingNoteSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by_user.username", read_only=True)
    approved_by_username = serializers.CharField(source="approved_by_user.username", read_only=True)

    class Meta:
        model = AdvisingNote
        fields = (
            "id",
            "note_text",
            "status",
            "created_by_username",
            "approved_by_username",
            "approved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "approved_at", "created_at", "updated_at")


class AdvisingNoteCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = AdvisingNote
        fields = ("id", "note_text")
