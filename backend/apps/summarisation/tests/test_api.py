import uuid

import pytest

from apps.accounts.constants import RoleCode
from apps.accounts.models import Role
from apps.students.models import StudentProfile
from apps.testutils import authenticated_client_for_user, create_user


@pytest.fixture
def roles(db):
    for code in RoleCode.values:
        Role.objects.get_or_create(code=code, defaults={"name": code.title()})


@pytest.fixture
def advisor_client(roles):
    user = create_user(username="advisor.api", primary_role=RoleCode.ADVISOR, full_name="Advisor API")
    return authenticated_client_for_user(user), user


@pytest.fixture
def admin_client(roles):
    user = create_user(username="admin.api", primary_role=RoleCode.ADMIN, full_name="Admin API")
    return authenticated_client_for_user(user), user


@pytest.fixture
def student_client(roles):
    user = create_user(username="student.api", primary_role=RoleCode.STUDENT, full_name="Student API")
    return authenticated_client_for_user(user), user


@pytest.fixture
def faculty_client(roles):
    user = create_user(username="faculty.api", primary_role=RoleCode.FACULTY, full_name="Faculty API")
    return authenticated_client_for_user(user), user


@pytest.mark.django_db
class TestSummariseEndpointAccess:
    def test_advisor_can_summarise(self, advisor_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = advisor_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Student missed three classes."}, format="json")
        assert response.status_code == 201
        assert "ai_output" in response.data

    def test_admin_can_summarise(self, admin_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = admin_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Helpdesk ticket about password reset."}, format="json")
        assert response.status_code == 201

    def test_student_denied(self, student_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = student_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Some text."}, format="json")
        assert response.status_code == 403

    def test_faculty_denied(self, faculty_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = faculty_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Some text."}, format="json")
        assert response.status_code == 403

    def test_empty_text_rejected(self, advisor_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = advisor_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": ""}, format="json")
        assert response.status_code == 400

    def test_text_too_long_rejected(self, advisor_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = advisor_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "x" * 5001}, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestSummariseApproveEndpoint:
    def test_approve_with_student_creates_note(self, advisor_client, settings, roles):
        settings.AI_PROVIDER = "deterministic"
        client, user = advisor_client
        student_user = create_user(username="student.approve", primary_role=RoleCode.STUDENT, full_name="Approve Student")
        student = StudentProfile.objects.create(
            user=student_user,
            student_number="APR001",
            date_of_birth="2000-01-01",
            gender="F",
            programme="BSc IT",
            year_of_study=1,
        )
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Meeting about course load.", "student_id": str(student.id)}, format="json")
        assert response.status_code == 201
        summarisation_id = response.data["id"]
        approve_response = client.post(
            f"/api/v1/ai/summarise/{summarisation_id}/approve/",
            {
                "key_issues": ["Course load too heavy"],
                "recommended_actions": ["Drop one elective"],
                "urgency_level": "Follow-up Needed",
            },
            format="json",
        )
        assert approve_response.status_code == 200
        assert approve_response.data["status"] == "APPROVED"
        assert approve_response.data["advising_note"] is not None

    def test_approve_without_student_no_note(self, admin_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, user = admin_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Admin helpdesk ticket."}, format="json")
        summarisation_id = response.data["id"]
        approve_response = client.post(
            f"/api/v1/ai/summarise/{summarisation_id}/approve/",
            {
                "key_issues": ["Access issue"],
                "recommended_actions": ["Reset account"],
                "urgency_level": "Routine",
            },
            format="json",
        )
        assert approve_response.status_code == 200
        assert approve_response.data["advising_note"] is None

    def test_student_cannot_approve(self, student_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = student_client
        response = client.post(f"/api/v1/ai/summarise/{uuid.uuid4()}/approve/", {}, format="json")
        assert response.status_code == 403
