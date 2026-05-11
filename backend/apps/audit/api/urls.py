from django.urls import path

from .views import AuditActivityDetailView, AuditActivityListView, AuditActivitySummaryView

urlpatterns = [
    path("admin/activity", AuditActivityListView.as_view(), name="admin-activity-list"),
    path("admin/activity/summary", AuditActivitySummaryView.as_view(), name="admin-activity-summary"),
    path("admin/activity/<uuid:event_id>", AuditActivityDetailView.as_view(), name="admin-activity-detail"),
]
