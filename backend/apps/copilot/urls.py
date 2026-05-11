from django.urls import path

from .views import (
    CopilotFeedbackView,
    CopilotQueryView,
    CopilotSessionArchiveView,
    CopilotSessionDetailView,
    CopilotSessionListCreateView,
)


urlpatterns = [
    path("ai/copilot/query", CopilotQueryView.as_view(), name="copilot-query"),
    path("ai/copilot/sessions", CopilotSessionListCreateView.as_view(), name="copilot-sessions-list-create"),
    path("ai/copilot/sessions/<uuid:session_id>", CopilotSessionDetailView.as_view(), name="copilot-session-detail"),
    path("ai/copilot/sessions/<uuid:session_id>/archive", CopilotSessionArchiveView.as_view(), name="copilot-session-archive"),
    path("ai/copilot/messages/<uuid:message_id>/feedback", CopilotFeedbackView.as_view(), name="copilot-message-feedback"),
]
