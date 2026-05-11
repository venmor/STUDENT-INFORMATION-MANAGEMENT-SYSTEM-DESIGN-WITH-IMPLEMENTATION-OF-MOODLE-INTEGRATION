from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AtRiskAlert
from .serializers import AtRiskAlertSerializer
from .services import acknowledge_alert


class AtRiskAlertListView(APIView):
    """GET /api/v1/advisor/at-risk/alerts - open alerts sorted by severity desc, date desc."""

    def get(self, request):
        alerts = AtRiskAlert.objects.filter(
            is_acknowledged=False, is_closed=False
        ).select_related("student", "student__user").order_by(
            "-severity", "-created_at"
        )
        return Response(AtRiskAlertSerializer(alerts, many=True).data)


class AtRiskAlertHistoryView(APIView):
    """GET /api/v1/advisor/at-risk/history - acknowledged/closed alerts."""

    def get(self, request):
        alerts = AtRiskAlert.objects.filter(
            is_acknowledged=True
        ).select_related("student", "student__user").order_by("-acknowledged_at")[:100]
        return Response(AtRiskAlertSerializer(alerts, many=True).data)


class AtRiskAlertAcknowledgeView(APIView):
    """POST /api/v1/advisor/at-risk/alerts/{id}/acknowledge - acknowledge an alert."""

    def post(self, request, alert_id):
        try:
            alert = acknowledge_alert(alert_id=alert_id, user=request.user)
        except AtRiskAlert.DoesNotExist:
            return Response(
                {"detail": "Alert not found or already acknowledged."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(AtRiskAlertSerializer(alert).data)
