from django.urls import path

from .views import AtRiskAlertAcknowledgeView, AtRiskAlertHistoryView, AtRiskAlertListView

urlpatterns = [
    path("advisor/at-risk/alerts", AtRiskAlertListView.as_view(), name="at-risk-alerts"),
    path("advisor/at-risk/history", AtRiskAlertHistoryView.as_view(), name="at-risk-history"),
    path("advisor/at-risk/alerts/<uuid:alert_id>/acknowledge", AtRiskAlertAcknowledgeView.as_view(), name="at-risk-acknowledge"),
]
