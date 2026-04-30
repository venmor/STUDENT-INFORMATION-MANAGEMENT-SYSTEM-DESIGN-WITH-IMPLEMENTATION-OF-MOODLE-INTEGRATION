from django.urls import path

from .views import (
    AcademicCalendarEventCancelView,
    AcademicCalendarEventDetailView,
    AcademicCalendarEventListCreateView,
    AcademicCalendarSummaryView,
)

urlpatterns = [
    path("calendar/events/", AcademicCalendarEventListCreateView.as_view(), name="calendar-events-list-create"),
    path("calendar/events/<uuid:event_id>/", AcademicCalendarEventDetailView.as_view(), name="calendar-event-detail"),
    path("calendar/events/<uuid:event_id>/cancel/", AcademicCalendarEventCancelView.as_view(), name="calendar-event-cancel"),
    path("calendar/summary/", AcademicCalendarSummaryView.as_view(), name="calendar-summary"),
]
