from django.urls import path

from .views import (
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
    NotificationSummaryView,
)

urlpatterns = [
    path("notifications", NotificationListView.as_view(), name="notifications-list"),
    path("notifications/summary", NotificationSummaryView.as_view(), name="notifications-summary"),
    path("notifications/<uuid:notification_id>/read", NotificationMarkReadView.as_view(), name="notification-read"),
    path("notifications/read-all", NotificationMarkAllReadView.as_view(), name="notifications-read-all"),
]
