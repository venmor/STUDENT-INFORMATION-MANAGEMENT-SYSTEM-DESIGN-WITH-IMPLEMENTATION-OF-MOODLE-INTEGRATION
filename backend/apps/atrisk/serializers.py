from rest_framework import serializers

from .models import AtRiskAlert


class AtRiskAlertSerializer(serializers.ModelSerializer):
    student_number = serializers.CharField(source="student.student_number", read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = AtRiskAlert
        fields = [
            "id",
            "student",
            "student_number",
            "student_name",
            "severity",
            "active_signals",
            "explanation",
            "provider",
            "model_name",
            "is_acknowledged",
            "acknowledged_by",
            "acknowledged_at",
            "is_closed",
            "closed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_student_name(self, obj) -> str:
        user = obj.student.user
        return user.full_name or user.username
