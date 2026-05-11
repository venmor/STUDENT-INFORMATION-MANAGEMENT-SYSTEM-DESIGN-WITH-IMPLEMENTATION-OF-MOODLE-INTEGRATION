from __future__ import annotations

from io import StringIO

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.accounts.constants import RoleCode
from apps.audit.models import AuditEvent
from apps.knowledge.models import KnowledgeChunk, KnowledgeIngestionRun, KnowledgeSource
from apps.knowledge.services import ingest_knowledge_base, test_knowledge_retrieval
from apps.knowledge.vector_store import InMemoryVectorStore
from apps.testutils import authenticated_client_for_user, create_user


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def local_vector_settings(settings):
    settings.EMBEDDING_PROVIDER = "deterministic"
    settings.EMBEDDING_VECTOR_SIZE = 32
    settings.KNOWLEDGE_VECTOR_STORE_PROVIDER = "memory"
    settings.QDRANT_COLLECTION = "test_knowledge"
    settings.KNOWLEDGE_CHUNK_TOKENS = 40
    settings.KNOWLEDGE_CHUNK_OVERLAP = 8


def test_seed_ingest_and_query_knowledge_demo_retrieves_drop_deadline():
    call_command("seed_knowledge_demo", stdout=StringIO())

    run = ingest_knowledge_base(vector_store=InMemoryVectorStore(collection_name="test_knowledge"), rebuild=True)
    results = test_knowledge_retrieval(
        "What is the deadline to drop a course?",
        vector_store=InMemoryVectorStore(collection_name="test_knowledge"),
        limit=3,
    )

    assert run.status == "SUCCEEDED"
    assert KnowledgeSource.objects.count() >= 5
    assert KnowledgeChunk.objects.count() > 0
    assert KnowledgeIngestionRun.objects.count() == 1
    assert results[0]["sourceTitle"] == "Academic Calendar Deadline Guide"
    assert "drop" in results[0]["text"].lower()
    assert AuditEvent.objects.filter(action="KNOWLEDGE_SOURCE_INGESTED").exists()


def test_knowledge_commands_print_clear_summaries():
    seed_stdout = StringIO()
    ingest_stdout = StringIO()
    query_stdout = StringIO()

    call_command("seed_knowledge_demo", stdout=seed_stdout)
    call_command("ingest_knowledge_base", "--rebuild", stdout=ingest_stdout)
    call_command("query_knowledge_base", "What is the deadline to drop a course?", stdout=query_stdout)

    assert "Knowledge demo sources are ready" in seed_stdout.getvalue()
    assert "Knowledge ingestion complete" in ingest_stdout.getvalue()
    assert "Academic Calendar Deadline Guide" in query_stdout.getvalue()
    assert "No LLM answer was generated" in query_stdout.getvalue()


def test_admin_knowledge_apis_are_admin_only_and_retrieval_only():
    call_command("seed_knowledge_demo", stdout=StringIO())
    ingest_knowledge_base(vector_store=InMemoryVectorStore(collection_name="test_knowledge"), rebuild=True)
    admin = create_user(username="knowledge-admin", primary_role=RoleCode.ADMIN, email="knowledge-admin@example.com")
    student = create_user(username="knowledge-student", primary_role=RoleCode.STUDENT, email="knowledge-student@example.com")

    admin_client = authenticated_client_for_user(admin)
    summary = admin_client.get("/api/v1/admin/knowledge/summary/")
    sources = admin_client.get("/api/v1/admin/knowledge/sources/")
    runs = admin_client.get("/api/v1/admin/knowledge/ingestion-runs/")
    query = admin_client.post(
        "/api/v1/admin/knowledge/test-query/",
        {"query": "What is the deadline to drop a course?", "limit": 3},
        format="json",
    )

    assert summary.status_code == 200
    assert summary.json()["vectorStore"]["provider"] == "memory"
    assert sources.status_code == 200
    assert runs.status_code == 200
    assert query.status_code == 200
    assert query.json()["generatedAnswer"] is None
    assert query.json()["results"][0]["sourceTitle"] == "Academic Calendar Deadline Guide"
    assert AuditEvent.objects.filter(action="KNOWLEDGE_RETRIEVAL_TESTED").exists()

    student_client = authenticated_client_for_user(student)
    assert student_client.get("/api/v1/admin/knowledge/summary/").status_code == 403
    assert APIClient().get("/api/v1/admin/knowledge/summary/").status_code == 401
