from django.urls import path

from .views import (
    AdminAnalyticsETLRunListView,
    AdminAnalyticsSnapshotDetailView,
    AdminAnalyticsSnapshotListView,
    AdminAnalyticsSummaryView,
)


urlpatterns = [
    path("admin/analytics/summary/", AdminAnalyticsSummaryView.as_view(), name="admin-analytics-summary"),
    path("admin/analytics/snapshots/", AdminAnalyticsSnapshotListView.as_view(), name="admin-analytics-snapshots"),
    path("admin/analytics/etl-runs/", AdminAnalyticsETLRunListView.as_view(), name="admin-analytics-etl-runs"),
    path("admin/analytics/snapshots/<uuid:snapshot_id>/", AdminAnalyticsSnapshotDetailView.as_view(), name="admin-analytics-snapshot-detail"),
]
