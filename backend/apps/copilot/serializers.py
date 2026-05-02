from __future__ import annotations

from rest_framework import serializers

from .models import (
    CopilotFeedback,
    CopilotFeedbackRating,
    CopilotMessage,
    CopilotMessageRole,
    CopilotSession,
)
from .safety import max_question_length, validate_question_text


class CopilotQuerySerializer(serializers.Serializer):
    question = serializers.CharField()
    sessionId = serializers.UUIDField(required=False, allow_null=True)

    def validate_question(self, value: str) -> str:
        return validate_question_text(value)


class CopilotSessionCreateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, allow_blank=True, max_length=120)


class CopilotFeedbackSerializer(serializers.Serializer):
    rating = serializers.ChoiceField(choices=CopilotFeedbackRating.choices)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=1000)


class CopilotFeedbackResponseSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = CopilotFeedback
        fields = ("id", "rating", "comment", "createdAt")


class CopilotMessageSerializer(serializers.ModelSerializer):
    sourceReferences = serializers.JSONField(source="source_references")
    modelName = serializers.CharField(source="model_name")
    retrievedChunkCount = serializers.IntegerField(source="retrieved_chunk_count")
    latencyMs = serializers.IntegerField(source="latency_ms", allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = CopilotMessage
        fields = (
            "id",
            "role",
            "content",
            "sourceReferences",
            "confidence",
            "provider",
            "modelName",
            "retrievedChunkCount",
            "latencyMs",
            "metadata",
            "createdAt",
        )


class CopilotSessionSerializer(serializers.ModelSerializer):
    studentId = serializers.UUIDField(source="student_id", allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")
    lastMessageAt = serializers.DateTimeField(source="last_message_at", allow_null=True)

    class Meta:
        model = CopilotSession
        fields = ("id", "studentId", "title", "status", "metadata", "createdAt", "updatedAt", "lastMessageAt")


class CopilotSessionDetailSerializer(CopilotSessionSerializer):
    messages = CopilotMessageSerializer(many=True)

    class Meta(CopilotSessionSerializer.Meta):
        fields = (*CopilotSessionSerializer.Meta.fields, "messages")


class CopilotAnswerResponseSerializer(serializers.Serializer):
    sessionId = serializers.UUIDField()
    messageId = serializers.UUIDField()
    answer = serializers.CharField()
    confidence = serializers.CharField()
    sources = serializers.ListField(child=serializers.DictField())
    suggestedNextActions = serializers.ListField(child=serializers.DictField())
    disclaimer = serializers.CharField()


def answer_to_payload(answer) -> dict:
    return {
        "sessionId": str(answer.session.id),
        "messageId": str(answer.assistant_message.id),
        "answer": answer.answer,
        "confidence": answer.confidence,
        "sources": answer.sources,
        "suggestedNextActions": answer.suggested_next_actions,
        "disclaimer": answer.disclaimer,
    }


def message_to_chat_payload(message: CopilotMessage) -> dict:
    return {
        "id": str(message.id),
        "role": message.role,
        "content": message.content,
        "sources": message.source_references if message.role == CopilotMessageRole.ASSISTANT else [],
        "confidence": message.confidence,
        "createdAt": message.created_at.isoformat(),
    }


def question_help_text() -> str:
    return f"Question must be non-empty and {max_question_length()} characters or fewer."
