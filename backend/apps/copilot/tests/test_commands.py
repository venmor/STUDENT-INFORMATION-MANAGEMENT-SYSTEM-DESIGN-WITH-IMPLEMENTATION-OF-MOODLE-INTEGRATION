from __future__ import annotations

from io import StringIO

import pytest
from django.core.management import call_command

from apps.copilot.models import CopilotSession


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def command_settings(settings):
    settings.AI_PROVIDER = "deterministic"
    settings.AI_MAX_CONTEXT_CHUNKS = 5
    settings.EMBEDDING_PROVIDER = "deterministic"
    settings.EMBEDDING_VECTOR_SIZE = 32
    settings.KNOWLEDGE_VECTOR_STORE_PROVIDER = "memory"
    settings.QDRANT_COLLECTION = "test_copilot_commands"
    settings.KNOWLEDGE_CHUNK_TOKENS = 40
    settings.KNOWLEDGE_CHUNK_OVERLAP = 8


def test_seed_and_test_copilot_query_commands_are_offline_and_repeatable():
    seed_stdout = StringIO()
    query_stdout = StringIO()

    call_command("seed_copilot_demo", stdout=seed_stdout)
    call_command("seed_copilot_demo", stdout=StringIO())
    call_command("test_copilot_query", "What is the deadline to drop a course?", stdout=query_stdout)

    assert "Co-pilot demo data is ready" in seed_stdout.getvalue()
    assert "student.demo1 / DemoPass123!" in seed_stdout.getvalue()
    assert CopilotSession.objects.filter(user__username="student.demo1").exists()
    assert "Answer:" in query_stdout.getvalue()
    assert "Confidence:" in query_stdout.getvalue()
    assert "Academic Calendar Deadline Guide" in query_stdout.getvalue()
    assert "Provider: deterministic" in query_stdout.getvalue()
