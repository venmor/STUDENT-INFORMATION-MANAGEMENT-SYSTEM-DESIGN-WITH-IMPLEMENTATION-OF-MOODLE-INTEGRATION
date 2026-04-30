from __future__ import annotations

from rest_framework import serializers

from apps.audit.models import AuditEvent
from apps.audit.services import sanitize_audit_metadata


class AuditEventSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    targetType = serializers.CharField(source="target_type")
    targetId = serializers.CharField(source="target_id")
    createdAt = serializers.DateTimeField(source="created_at")
    ipAddress = serializers.IPAddressField(source="ip_address", allow_null=True, required=False)
    userAgent = serializers.CharField(source="user_agent")
    metadata = serializers.SerializerMethodField()

    class Meta:
        model = AuditEvent
        fields = [
            "id",
            "actor",
            "category",
            "action",
            "severity",
            "summary",
            "targetType",
            "targetId",
            "metadata",
            "ipAddress",
            "userAgent",
            "createdAt",
        ]

    def get_actor(self, obj: AuditEvent):
        if obj.actor_id and obj.actor is not None:
            return {
                "id": obj.actor_id,
                "username": obj.actor.username,
                "fullName": obj.actor.full_name,
                "role": obj.actor.primary_role,
            }
        if obj.actor_username:
            return {
                "id": None,
                "username": obj.actor_username,
                "fullName": obj.actor_username,
                "role": obj.actor_role,
            }
        return None

    def get_metadata(self, obj: AuditEvent) -> dict:
        return sanitize_audit_metadata(obj.metadata)
