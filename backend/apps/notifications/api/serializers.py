from __future__ import annotations

from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actionLabel = serializers.CharField(source="action_label")
    actionUrl = serializers.CharField(source="action_url")
    isRead = serializers.BooleanField(source="is_read")
    readAt = serializers.DateTimeField(source="read_at", allow_null=True)
    createdAt = serializers.DateTimeField(source="created_at")
    sourceType = serializers.CharField(source="source_type")
    sourceId = serializers.CharField(source="source_id")

    class Meta:
        model = Notification
        fields = (
            "id",
            "category",
            "severity",
            "title",
            "message",
            "actionLabel",
            "actionUrl",
            "isRead",
            "readAt",
            "createdAt",
            "sourceType",
            "sourceId",
        )
