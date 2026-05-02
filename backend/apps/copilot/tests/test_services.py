from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.academics.models import Course, CourseSection, CourseSectionStatus, Enrollment, EnrollmentStatus, GradeRecord, GradeStatus
from apps.accounts.constants import RoleCode
from apps.analytics.models import AnalyticsETLRun, StudentAnalyticsSnapshot
from apps.copilot.models import AIAuditAction, AIAuditLog, CopilotConfidence, CopilotProvider
from apps.copilot.services import answer_copilot_question
from apps.documents.models import DocumentStatus, DocumentType, DocumentVisibility, StudentDocument
from apps.knowledge.services import ingest_knowledge_base, seed_demo_knowledge_sources
from apps.knowledge.vector_store import InMemoryVectorStore
from apps.students.models import AcademicStanding, StudentProfile
from apps.testutils import create_user


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def copilot_settings(settings):
    settings.AI_PROVIDER = "deterministic"
    settings.AI_MAX_CONTEXT_CHUNKS = 5
    settings.AI_MAX_QUESTION_LENGTH = 500
    settings.COPILOT_LOW_CONFIDENCE_THRESHOLD = 0.2
    settings.EMBEDDING_PROVIDER = "deterministic"
    settings.EMBEDDING_VECTOR_SIZE = 32
    settings.KNOWLEDGE_VECTOR_STORE_PROVIDER = "memory"
    settings.QDRANT_COLLECTION = "test_copilot"
    settings.KNOWLEDGE_CHUNK_TOKENS = 40
    settings.KNOWLEDGE_CHUNK_OVERLAP = 8


def create_student_user(username: str = "copilot.student") -> StudentProfile:
    user = create_user(username=username, primary_role=RoleCode.STUDENT, email=f"{username}@example.edu", full_name="Copilot Student")
    return StudentProfile.objects.create(
        user=user,
        student_number=f"2026/CP/{username[-1].upper() if username[-1].isalnum() else '1'}",
        national_id=f"NRC-{username}",
        date_of_birth=date(2004, 1, 15),
        gender="Female",
        programme="BSc Computer Science",
        year_of_study=3,
        academic_standing=AcademicStanding.GOOD_STANDING,
        cumulative_gpa=Decimal("3.20"),
        is_active=True,
    )


def create_safe_context_records(student: StudentProfile) -> None:
    faculty = create_user(username="copilot.faculty", primary_role=RoleCode.FACULTY, email="copilot.faculty@example.edu")
    course = Course.objects.create(
        course_code="CPL410",
        course_title="Co-pilot Systems",
        department="Computer Science",
        credit_hours=3,
        programme_code="BSc Computer Science",
        max_capacity=40,
    )
    section = CourseSection.objects.create(
        course=course,
        section_code="A1",
        faculty_user=faculty,
        room="Lab 1",
        semester="Semester 1",
        academic_year="2026/2027",
        max_capacity=40,
        registration_opens_at=timezone.now() - timedelta(days=7),
        registration_closes_at=timezone.now() + timedelta(days=7),
        drop_deadline=timezone.now() + timedelta(days=21),
        status=CourseSectionStatus.ACTIVE,
    )
    Enrollment.objects.create(
        student=student,
        section=section,
        enrollment_status=EnrollmentStatus.ENROLLED,
        actor_role=RoleCode.ADMIN,
        actor_user=None,
        is_active=True,
    )
    GradeRecord.objects.create(
        student=student,
        section=section,
        numeric_score=Decimal("88.00"),
        letter_grade="A",
        grade_points=Decimal("4.00"),
        grade_status=GradeStatus.OFFICIAL,
        entered_by_user=faculty,
        officialised_by_user=faculty,
        officialised_at=timezone.now(),
    )
    StudentDocument.objects.create(
        student=student,
        uploaded_by=student.user,
        document_type=DocumentType.TRANSCRIPT,
        title="Student-visible transcript copy",
        description="Do not pass this content to AI.",
        file="student_documents/demo/transcript.pdf",
        original_filename="transcript.pdf",
        content_type="application/pdf",
        file_size=1234,
        visibility=DocumentVisibility.STUDENT_VISIBLE,
        status=DocumentStatus.REJECTED,
        review_note="Private review note that must not enter prompts.",
    )
    run = AnalyticsETLRun.objects.create(status="SUCCEEDED", completed_at=timezone.now())
    StudentAnalyticsSnapshot.objects.create(
        student=student,
        user=student.user,
        academic_year="2026/2027",
        semester="Semester 1",
        programme=student.programme,
        year_of_study=student.year_of_study,
        academic_standing=student.academic_standing,
        attendance_average=Decimal("87.50"),
        financial_flag_count=0,
        active_enrollment_count=1,
        draft_grade_count=0,
        official_grade_count=1,
        gpa=Decimal("3.20"),
        moodle_snapshot_count=2,
        source_run=run,
    )


def ingest_demo_knowledge() -> None:
    seed_demo_knowledge_sources()
    ingest_knowledge_base(vector_store=InMemoryVectorStore(collection_name="test_copilot"), rebuild=True)


def test_deterministic_provider_returns_source_grounded_answer_and_audit_log():
    student = create_student_user()
    create_safe_context_records(student)
    ingest_demo_knowledge()

    response = answer_copilot_question(user=student.user, question="What is the deadline to drop a course?")

    assert response.answer
    assert response.confidence in {CopilotConfidence.HIGH, CopilotConfidence.MEDIUM}
    assert response.sources
    assert response.sources[0]["title"] == "Academic Calendar Deadline Guide"
    assert response.session.user == student.user
    assert response.assistant_message.provider == CopilotProvider.DETERMINISTIC
    assert response.assistant_message.retrieved_chunk_count > 0
    assert AIAuditLog.objects.filter(action=AIAuditAction.COPILOT_QUERY, user=student.user).exists()
    assert AIAuditLog.objects.filter(action=AIAuditAction.COPILOT_RESPONSE, user=student.user).exists()


def test_no_source_query_returns_unsupported_fallback_without_inventing_answer(settings):
    settings.COPILOT_LOW_CONFIDENCE_THRESHOLD = 0.99
    student = create_student_user()

    response = answer_copilot_question(user=student.user, question="Can the co-pilot approve my scholarship appeal?")

    assert response.confidence == CopilotConfidence.UNSUPPORTED
    assert "I don't have enough information" in response.answer
    assert "Registrar" in response.answer
    assert response.sources == []
    assert AIAuditLog.objects.filter(action=AIAuditAction.COPILOT_LOW_CONFIDENCE, user=student.user).exists()


def test_safe_student_context_excludes_private_document_contents_and_review_notes():
    student = create_student_user()
    create_safe_context_records(student)
    ingest_demo_knowledge()

    response = answer_copilot_question(user=student.user, question="What should I do if my document was rejected?")

    prompt_context = response.assistant_message.metadata["promptContextPreview"]
    assert "Student-visible transcript copy" not in prompt_context
    assert "Private review note" not in prompt_context
    assert "documentStatusSummary" in prompt_context
    assert response.suggested_next_actions[0]["url"] == "/documents"


def test_provider_failure_is_handled_safely(monkeypatch):
    student = create_student_user()
    ingest_demo_knowledge()

    class FailingProvider:
        provider = CopilotProvider.OPENAI_COMPATIBLE
        model_name = "broken-model"

        def generate(self, *, question, retrieved_chunks, safe_student_context, system_prompt):
            raise RuntimeError("boom secret-token-value")

    monkeypatch.setattr("apps.copilot.services.get_copilot_provider", lambda: FailingProvider())

    response = answer_copilot_question(user=student.user, question="How do I register for courses?")

    assert response.confidence == CopilotConfidence.LOW
    assert "temporarily unavailable" in response.answer
    audit = AIAuditLog.objects.get(action=AIAuditAction.COPILOT_PROVIDER_ERROR)
    assert "secret-token-value" not in str(audit.metadata)


def test_retrieval_uses_configured_top_k_limit(monkeypatch):
    student = create_student_user()

    observed = {}

    def fake_retrieval(query, *, limit, source_type="", actor=None, request=None):
        observed["limit"] = limit
        return [
            {
                "chunkId": "chunk-1",
                "sourceId": "source-1",
                "sourceTitle": "Registration Procedures",
                "sourceType": "REGISTRATION_PROCEDURES",
                "score": 0.82,
                "text": "Students register for courses through the SIS registration workflow.",
            }
        ]

    monkeypatch.setattr("apps.copilot.services.test_knowledge_retrieval", fake_retrieval)

    response = answer_copilot_question(user=student.user, question="How do I register for courses?")

    assert observed["limit"] == 5
    assert response.sources[0]["title"] == "Registration Procedures"


def test_seed_copilot_demo_creates_repeatable_session_and_knowledge_data():
    call_command("seed_copilot_demo")

    student = StudentProfile.objects.get(user__username="student.demo1")
    response = answer_copilot_question(user=student.user, question="What are my current enrolled courses?")

    assert response.session.user == student.user
    assert response.sources
