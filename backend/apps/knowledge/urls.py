from django.urls import path

from .views import (
    AdminKnowledgeIngestionRunListView,
    AdminKnowledgeSourceListView,
    AdminKnowledgeSummaryView,
    AdminKnowledgeTestQueryView,
)


urlpatterns = [
    path("admin/knowledge/summary/", AdminKnowledgeSummaryView.as_view(), name="admin-knowledge-summary"),
    path("admin/knowledge/sources/", AdminKnowledgeSourceListView.as_view(), name="admin-knowledge-sources"),
    path("admin/knowledge/ingestion-runs/", AdminKnowledgeIngestionRunListView.as_view(), name="admin-knowledge-ingestion-runs"),
    path("admin/knowledge/test-query/", AdminKnowledgeTestQueryView.as_view(), name="admin-knowledge-test-query"),
]
