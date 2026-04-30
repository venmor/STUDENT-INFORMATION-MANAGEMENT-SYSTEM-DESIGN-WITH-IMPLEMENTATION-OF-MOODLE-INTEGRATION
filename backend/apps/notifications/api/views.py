from __future__ import annotations

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import (
    Notification,
    NotificationCategory,
    NotificationSeverity,
)

from .serializers import NotificationSerializer


def notification_queryset_for_user(user):
    return Notification.objects.filter(recipient=user).order_by("-created_at", "-id")


def bounded_limit(raw_limit: str | None, *, default: int = 50, maximum: int = 100) -> int:
    try:
        requested = int(raw_limit or default)
    except (TypeError, ValueError):
        return default
    return max(1, min(requested, maximum))


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = notification_queryset_for_user(request.user)
        status_filter = (request.query_params.get("status") or "all").lower()
        category = request.query_params.get("category")
        severity = request.query_params.get("severity")
        limit = bounded_limit(request.query_params.get("limit"))

        if status_filter == "unread":
            queryset = queryset.filter(is_read=False)
        elif status_filter == "read":
            queryset = queryset.filter(is_read=True)

        if category in NotificationCategory.values:
            queryset = queryset.filter(category=category)
        if severity in NotificationSeverity.values:
            queryset = queryset.filter(severity=severity)

        return Response(NotificationSerializer(queryset[:limit], many=True).data)


class NotificationSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = notification_queryset_for_user(request.user)
        counts = {
            item["category"]: item["count"]
            for item in queryset.order_by().values("category").annotate(count=Count("id"))
        }
        by_category = {
            category: counts.get(category, 0)
            for category in NotificationCategory.values
        }
        latest = NotificationSerializer(queryset[:5], many=True).data
        return Response(
            {
                "unreadCount": queryset.filter(is_read=False).count(),
                "latest": latest,
                "byCategory": by_category,
            }
        )


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at", "updated_at"])
            try:
                from apps.audit.services import record_audit_event_safely

                record_audit_event_safely(
                    actor=request.user,
                    category="NOTIFICATION",
                    action="NOTIFICATION_READ",
                    summary=f"Notification {notification.title} was marked as read.",
                    target_type="Notification",
                    target_id=str(notification.id),
                    severity="INFO",
                    metadata={
                        "category": notification.category,
                        "severity": notification.severity,
                        "sourceType": notification.source_type,
                        "sourceId": notification.source_id,
                    },
                    request=request,
                )
            except Exception:
                pass
        return Response(NotificationSerializer(notification).data)


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        now = timezone.now()
        updated = Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True,
            read_at=now,
            updated_at=now,
        )
        try:
            from apps.audit.services import record_audit_event_safely

            record_audit_event_safely(
                actor=request.user,
                category="NOTIFICATION",
                action="NOTIFICATIONS_READ_ALL",
                summary=f"{updated} notifications were marked as read.",
                target_type="Notification",
                target_id="bulk-read",
                severity="INFO",
                metadata={"updatedCount": updated},
                request=request,
            )
        except Exception:
            pass
        return Response({"updatedCount": updated})
