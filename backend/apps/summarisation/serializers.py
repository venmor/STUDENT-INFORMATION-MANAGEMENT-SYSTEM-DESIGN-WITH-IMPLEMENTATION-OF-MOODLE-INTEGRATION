from rest_framework import serializers

from .models import SummarisationRequest, UrgencyLevel
from .prompts import MAX_INPUT_LENGTH


class SummariseInputSerializer(serializers.Serializer):
    raw_text = serializers.CharField(max_length=MAX_INPUT_LENGTH)
    student_id = serializers.UUIDField(required=False, allow_null=True)


class SummarisationOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummarisationRequest
        fields = [
            "id",
            "raw_input_text",
            "ai_output",
            "human_edited_output",
            "status",
            "provider",
            "model_name",
            "latency_ms",
            "student",
            "advising_note",
            "created_at",
            "approved_at",
        ]
        read_only_fields = fields


class SummariseApproveInputSerializer(serializers.Serializer):
    key_issues = serializers.ListField(child=serializers.CharField(max_length=500), max_length=5)
    recommended_actions = serializers.ListField(child=serializers.CharField(max_length=500), max_length=5)
    urgency_level = serializers.ChoiceField(choices=UrgencyLevel.choices)
