from django.urls import path

from .views import (
    WellbeingCheckInDeleteView,
    WellbeingConsentView,
    WellbeingCoordinatorAlertsView,
    WellbeingHistoryPurgeView,
    WellbeingHistoryView,
    WellbeingReportingTrendsView,
    WellbeingTriageView,
)

urlpatterns = [
    path("wellbeing/consent", WellbeingConsentView.as_view(), name="wellbeing-consent"),
    path("ai/wellbeing/triage", WellbeingTriageView.as_view(), name="wellbeing-triage"),
    path("wellbeing/history", WellbeingHistoryView.as_view(), name="wellbeing-history"),
    path("wellbeing/history/purge", WellbeingHistoryPurgeView.as_view(), name="wellbeing-purge"),
    path("wellbeing/history/<uuid:checkin_id>", WellbeingCheckInDeleteView.as_view(), name="wellbeing-delete"),
    path("wellbeing/coordinator/alerts", WellbeingCoordinatorAlertsView.as_view(), name="wellbeing-coordinator-alerts"),
    path("wellbeing/reporting/trends", WellbeingReportingTrendsView.as_view(), name="wellbeing-reporting-trends"),
]
