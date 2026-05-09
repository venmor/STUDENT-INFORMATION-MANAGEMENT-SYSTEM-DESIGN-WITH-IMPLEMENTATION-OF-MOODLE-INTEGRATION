from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.constants import RoleCode
from apps.copilot.models import CopilotConfidence, CopilotMessage, CopilotMessageRole, CopilotSession
from apps.knowledge.services import ingest_knowledge_base, seed_demo_knowledge_sources
from apps.knowledge.vector_store import InMemoryVectorStore
from apps.students.models import AcademicStanding, StudentProfile
from apps.testutils import authenticated_client_for_user, create_user


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def copilot_api_settings(settings):
    settings.AI_PROVIDER = "deterministic"
    settings.AI_FALLBACK_PROVIDER = ""
    settings.AI_RETRY_ATTEMPTS = 0
    settings.AI_RETRY_DELAY_SECONDS = 0
    settings.AI_MAX_CONTEXT_CHUNKS = 5
    settings.AI_MAX_QUESTION_LENGTH = 120
    settings.COPILOT_LOW_CONFIDENCE_THRESHOLD = 0.2
    settings.EMBEDDING_PROVIDER = "deterministic"
    settings.EMBEDDING_VECTOR_SIZE = 32
    settings.KNOWLEDGE_VECTOR_STORE_PROVIDER = "memory"
    settings.QDRANT_COLLECTION = "test_copilot_api"
    settings.KNOWLEDGE_CHUNK_TOKENS = 40
    settings.KNOWLEDGE_CHUNK_OVERLAP = 8


def create_student(username: str, student_number: str) -> StudentProfile:
    user = create_user(username=username, primary_role=RoleCode.STUDENT, email=f"{username}@example.edu", full_name=username.title())
    return StudentProfile.objects.create(
        user=user,
        student_number=student_number,
        national_id=f"NRC-{student_number}",
        date_of_birth=date(2004, 1, 15),
        gender="Male",
        programme="BSc Computer Science",
        year_of_study=2,
        academic_standing=AcademicStanding.GOOD_STANDING,
        cumulative_gpa=Decimal("3.10"),
        is_active=True,
    )


def ingest_demo_knowledge() -> None:
    seed_demo_knowledge_sources()
    ingest_knowledge_base(vector_store=InMemoryVectorStore(collection_name="test_copilot_api"), rebuild=True)


def test_student_can_create_query_list_retrieve_archive_and_rate_session():
    student = create_student("copilot.api.student", "2026/API/001")
    ingest_demo_knowledge()
    client = authenticated_client_for_user(student.user)

    create_response = client.post("/api/v1/ai/copilot/sessions", {"title": "Registration help"}, format="json")
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    query_response = client.post(
        "/api/v1/ai/copilot/query",
        {"question": "What is the deadline to drop a course?", "sessionId": session_id},
        format="json",
    )

    assert query_response.status_code == 200
    payload = query_response.json()
    assert payload["sessionId"] == session_id
    assert payload["answer"]
    assert payload["confidence"] in {CopilotConfidence.HIGH, CopilotConfidence.MEDIUM}
    assert payload["sources"][0]["title"] == "Academic Calendar Deadline Guide"
    assert payload["suggestedNextActions"]
    assert "Registrar" in payload["disclaimer"]

    list_response = client.get("/api/v1/ai/copilot/sessions")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == session_id

    detail_response = client.get(f"/api/v1/ai/copilot/sessions/{session_id}")
    assert detail_response.status_code == 200
    assert len(detail_response.json()["messages"]) == 2

    message_id = payload["messageId"]
    feedback_response = client.post(
        f"/api/v1/ai/copilot/messages/{message_id}/feedback",
        {"rating": "HELPFUL", "comment": "Clear source."},
        format="json",
    )
    assert feedback_response.status_code == 201

    archive_response = client.post(f"/api/v1/ai/copilot/sessions/{session_id}/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["status"] == "ARCHIVED"


def test_unauthenticated_and_non_student_users_are_denied():
    advisor = create_user(username="copilot.advisor", primary_role=RoleCode.ADVISOR, email="copilot.advisor@example.edu")
    faculty = create_user(username="copilot.faculty.user", primary_role=RoleCode.FACULTY, email="copilot.faculty.user@example.edu")

    assert APIClient().post("/api/v1/ai/copilot/query", {"question": "How do I register?"}, format="json").status_code == 401
    assert authenticated_client_for_user(advisor).post("/api/v1/ai/copilot/query", {"question": "How do I register?"}, format="json").status_code == 403
    assert authenticated_client_for_user(faculty).get("/api/v1/ai/copilot/sessions").status_code == 403


def test_student_cannot_access_another_students_session_or_feedback_message():
    owner = create_student("copilot.owner", "2026/API/002")
    other = create_student("copilot.other", "2026/API/003")
    session = CopilotSession.objects.create(user=owner.user, student=owner, title="Owner session")
    message = CopilotMessage.objects.create(
        session=session,
        role=CopilotMessageRole.ASSISTANT,
        content="Owner answer",
        confidence=CopilotConfidence.HIGH,
        provider="deterministic",
    )
    other_client = authenticated_client_for_user(other.user)

    assert other_client.get(f"/api/v1/ai/copilot/sessions/{session.id}").status_code == 404
    assert other_client.post(f"/api/v1/ai/copilot/sessions/{session.id}/archive").status_code == 404
    assert other_client.post(f"/api/v1/ai/copilot/messages/{message.id}/feedback", {"rating": "HELPFUL"}, format="json").status_code == 404


def test_query_validation_rejects_empty_and_overly_long_questions():
    student = create_student("copilot.validation", "2026/API/004")
    client = authenticated_client_for_user(student.user)

    empty = client.post("/api/v1/ai/copilot/query", {"question": "   "}, format="json")
    too_long = client.post("/api/v1/ai/copilot/query", {"question": "x" * 121}, format="json")

    assert empty.status_code == 400
    assert too_long.status_code == 400


def test_low_confidence_payload_contains_disclaimer_and_workflow_links(settings):
    settings.COPILOT_LOW_CONFIDENCE_THRESHOLD = 0.99
    student = create_student("copilot.low", "2026/API/005")
    client = authenticated_client_for_user(student.user)

    response = client.post(
        "/api/v1/ai/copilot/query",
        {"question": "Can you approve my document now?"},
        format="json",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["confidence"] == CopilotConfidence.UNSUPPORTED
    assert payload["sources"] == []
    assert "Registrar" in payload["disclaimer"]
    assert any(action["url"] == "/documents" for action in payload["suggestedNextActions"])
