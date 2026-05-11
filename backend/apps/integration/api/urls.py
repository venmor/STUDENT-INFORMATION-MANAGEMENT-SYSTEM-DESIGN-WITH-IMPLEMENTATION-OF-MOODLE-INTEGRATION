from django.urls import path

from .views import (
    MoodleCourseMapListView,
    MoodleEngagementRunListView,
    MoodleEngagementSnapshotListView,
    MoodleOutboxEventListView,
    MoodleOutboxEventRetryView,
    MoodleSyncSummaryView,
    MoodleUserMapListView,
)


urlpatterns = [
    path("integration/moodle/summary", MoodleSyncSummaryView.as_view(), name="moodle-sync-summary"),
    path("integration/moodle/outbox-events", MoodleOutboxEventListView.as_view(), name="moodle-sync-outbox-events"),
    path(
        "integration/moodle/outbox-events/<uuid:event_id>/retry",
        MoodleOutboxEventRetryView.as_view(),
        name="moodle-sync-outbox-event-retry",
    ),
    path("integration/moodle/user-maps", MoodleUserMapListView.as_view(), name="moodle-sync-user-maps"),
    path("integration/moodle/course-maps", MoodleCourseMapListView.as_view(), name="moodle-sync-course-maps"),
    path("integration/moodle/engagement-runs", MoodleEngagementRunListView.as_view(), name="moodle-sync-engagement-runs"),
    path(
        "integration/moodle/engagement-snapshots",
        MoodleEngagementSnapshotListView.as_view(),
        name="moodle-sync-engagement-snapshots",
    ),
]
