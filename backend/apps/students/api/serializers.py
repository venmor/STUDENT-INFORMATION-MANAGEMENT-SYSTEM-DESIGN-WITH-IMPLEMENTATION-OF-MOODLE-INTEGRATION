from __future__ import annotations

from rest_framework import serializers

from apps.accounts.models import User
from apps.students.models import (
    AdvisorAssignment,
    AdvisingNote,
    FinancialFlag,
    StudentCorrectionRequest,
    StudentCorrectionRequestStatus,
    StudentProfile,
)


class StudentProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    attendance_flags = serializers.SerializerMethodField()
    attendance_percentages = serializers.SerializerMethodField()

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
            "attendance_percentages",
        )
        read_only_fields = ("cumulative_gpa", "attendance_flags", "attendance_percentages", "is_active")

    def validate(self, attrs):
        if self.instance is None:
            return attrs

        academic_standing = attrs.get("academic_standing")
        if academic_standing and academic_standing != self.instance.academic_standing:
            override_reason = attrs.get("standing_override_reason", "").strip()
            if not override_reason:
                raise serializers.ValidationError(
                    {"standing_override_reason": "A reason is required when overriding academic standing."}
                )

        return attrs

    def get_attendance_flags(self, obj):
        from apps.academics.services import calculate_attendance_flags

        return calculate_attendance_flags(obj)

    def get_attendance_percentages(self, obj):
        from apps.academics.services import calculate_attendance_percentages

        return calculate_attendance_percentages(obj)


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


class FinancialFlagUpdateSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False)
    cleared_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        return attrs


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


class AdvisingNoteUpdateSerializer(serializers.Serializer):
    note_text = serializers.CharField()


class StudentCorrectionRequestSerializer(serializers.ModelSerializer):
    reviewed_by_username = serializers.CharField(source="reviewed_by_user.username", read_only=True)

    class Meta:
        model = StudentCorrectionRequest
        fields = (
            "id",
            "requested_changes",
            "justification",
            "status",
            "review_note",
            "reviewed_by_username",
            "reviewed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "review_note",
            "reviewed_by_username",
            "reviewed_at",
            "created_at",
            "updated_at",
        )


class StudentCorrectionRequestCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = StudentCorrectionRequest
        fields = ("id", "requested_changes", "justification")


class StudentCorrectionRequestReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=(
            StudentCorrectionRequestStatus.APPROVED,
            StudentCorrectionRequestStatus.REJECTED,
        )
    )
    review_note = serializers.CharField(required=False, allow_blank=True)
