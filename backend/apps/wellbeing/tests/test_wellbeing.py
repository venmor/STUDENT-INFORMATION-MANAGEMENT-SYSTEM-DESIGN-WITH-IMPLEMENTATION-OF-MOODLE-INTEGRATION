import pytest
from apps.accounts.constants import RoleCode
from apps.testutils import create_user, authenticated_client_for_user
from apps.students.models import StudentProfile
from apps.wellbeing.models import WellbeingCheckIn, TriageClass, WellbeingConsent
from datetime import date

pytestmark = pytest.mark.django_db

@pytest.fixture
def student_user():
    user = create_user(username="wb.student", primary_role=RoleCode.STUDENT)
    StudentProfile.objects.create(
        user=user,
        student_number="S-WB-01",
        national_id="WB-01",
        date_of_birth=date(2004, 1, 1),
        gender="F",
        programme="BSc CS",
        year_of_study=1
    )
    return user

@pytest.fixture
def coordinator_user():
    user = create_user(username="wb.coordinator", primary_role=RoleCode.ADVISOR)
    user.capabilities.create(capability_name="wellbeing_coordinator")
    return user

def test_consent_required_for_triage(student_user):
    client = authenticated_client_for_user(student_user)
    response = client.post("/api/v1/ai/wellbeing/triage", {"mood_rating": 3})
    assert response.status_code == 403

def test_student_can_opt_in_and_triage(student_user):
    client = authenticated_client_for_user(student_user)

    # Opt-in
    client.post("/api/v1/wellbeing/consent", {"is_enabled": True})
    assert WellbeingConsent.objects.get(student=student_user.student_profile).is_enabled is True

    # Normal triage
    response = client.post("/api/v1/ai/wellbeing/triage", {"mood_rating": 4, "comment": "Doing fine"})
    assert response.status_code == 201
    assert response.data["triage_class"] == "NORMAL"

def test_deterministic_escalation(student_user, coordinator_user):
    client = authenticated_client_for_user(student_user)
    client.post("/api/v1/wellbeing/consent", {"is_enabled": True})

    # Rating 1 triggers escalation
    response = client.post("/api/v1/ai/wellbeing/triage", {"mood_rating": 1})
    assert response.data["triage_class"] == "ESCALATE"

    # Keywords trigger escalation
    response = client.post("/api/v1/ai/wellbeing/triage", {"mood_rating": 5, "comment": "I want to harm myself"})
    assert response.data["triage_class"] == "ESCALATE"

def test_coordinator_access(coordinator_user, student_user):
    # Setup an escalation
    student_user.student_profile.wellbeing_consent = WellbeingConsent.objects.create(student=student_user.student_profile, is_enabled=True)
    WellbeingCheckIn.objects.create(
        student=student_user.student_profile,
        mood_rating=1,
        triage_class=TriageClass.ESCALATE
    )

    client = authenticated_client_for_user(coordinator_user)
    response = client.get("/api/v1/wellbeing/coordinator/alerts")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["student_number"] == "S-WB-01"

def test_student_can_delete_history(student_user):
    client = authenticated_client_for_user(student_user)
    client.post("/api/v1/wellbeing/consent", {"is_enabled": True})
    checkin = WellbeingCheckIn.objects.create(
        student=student_user.student_profile,
        mood_rating=3,
        comment="Secrets"
    )

    response = client.delete(f"/api/v1/wellbeing/history/{checkin.id}")
    assert response.status_code == 204

    checkin.refresh_from_db()
    assert checkin.is_deleted_by_student is True
    assert checkin.comment == "[DELETED]"

def test_admin_can_view_trends(student_user):
    admin = create_user(username="wb.admin", primary_role=RoleCode.ADMIN, is_staff=True)
    client = authenticated_client_for_user(student_user)
    client.post("/api/v1/wellbeing/consent", {"is_enabled": True})
    client.post("/api/v1/ai/wellbeing/triage", {"mood_rating": 4})

    admin_client = authenticated_client_for_user(admin)
    response = admin_client.get("/api/v1/wellbeing/reporting/trends")
    assert response.status_code == 200
    assert len(response.data) > 0
