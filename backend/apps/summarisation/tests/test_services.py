import pytest
from django.test import override_settings

from apps.accounts.constants import RoleCode
from apps.accounts.models import Role
from apps.copilot.models import AIAuditLog, AIAuditAction
from apps.students.models import AdvisingNoteStatus
from apps.summarisation.models import SummarisationStatus
from apps.summarisation.services import create_summarisation_request, approve_summarisation, validate_input_text
from apps.testutils import create_user


@pytest.fixture
def roles(db):
    for code in RoleCode.values:
        Role.objects.get_or_create(code=code, defaults={"name": code.title()})


@pytest.fixture
def advisor_user(roles):
    return create_user(username="advisor.sumtest", primary_role=RoleCode.ADVISOR, full_name="Advisor Test")


@pytest.fixture
def student_profile(roles):
    from apps.students.models import StudentProfile
    student_user = create_user(username="student.sumtest", primary_role=RoleCode.STUDENT, full_name="Student SumTest")
    return StudentProfile.objects.create(
        user=student_user,
        student_number="SUM001",
        date_of_birth="2000-01-01",
        gender="M",
        programme="BSc Computer Science",
        year_of_study=2,
    )


@pytest.mark.django_db
@override_settings(AI_PROVIDER="deterministic")
def test_create_summarisation_request_deterministic(advisor_user):
    result = create_summarisation_request(
        user=advisor_user,
        raw_text="Student is struggling with calculus and has missed three classes. Need to discuss study plan.",
    )
    assert result.status == SummarisationStatus.PENDING
    assert result.provider == "deterministic"
    assert "key_issues" in result.ai_output
    assert "recommended_actions" in result.ai_output
    assert result.ai_output["urgency_level"] in {"Routine", "Follow-up Needed", "Urgent"}
    audit = AIAuditLog.objects.filter(action=AIAuditAction.SUMMARISATION_REQUEST).first()
    assert audit is not None
    assert audit.user == advisor_user


@pytest.mark.django_db
@override_settings(AI_PROVIDER="deterministic")
def test_create_summarisation_request_with_student(advisor_user, student_profile):
    result = create_summarisation_request(
        user=advisor_user,
        raw_text="Student wants to drop a course past the deadline. Financial aid implications discussed.",
        student=student_profile,
    )
    assert result.student == student_profile


@pytest.mark.django_db
@override_settings(AI_PROVIDER="deterministic")
def test_approve_summarisation_creates_advising_note(advisor_user, student_profile):
    summarisation = create_summarisation_request(
        user=advisor_user,
        raw_text="Discussed graduate school preparation and recommendation letters.",
        student=student_profile,
    )
    approved = approve_summarisation(
        user=advisor_user,
        summarisation=summarisation,
        human_edited_output={
            "key_issues": ["Needs recommendation letter for grad school"],
            "recommended_actions": ["Connect with research supervisor"],
            "urgency_level": "Routine",
        },
    )
    assert approved.status == SummarisationStatus.APPROVED
    assert approved.advising_note is not None
    note = approved.advising_note
    assert note.status == AdvisingNoteStatus.APPROVED
    assert note.student == student_profile
    assert "recommendation letter" in note.note_text
    audit = AIAuditLog.objects.filter(action=AIAuditAction.SUMMARISATION_APPROVED).first()
    assert audit is not None
    assert audit.metadata.get("approvedBy") == str(advisor_user.id)


@pytest.mark.django_db
@override_settings(AI_PROVIDER="deterministic")
def test_approve_without_student_no_advising_note(advisor_user):
    summarisation = create_summarisation_request(
        user=advisor_user,
        raw_text="General helpdesk ticket about system access.",
    )
    approved = approve_summarisation(
        user=advisor_user,
        summarisation=summarisation,
        human_edited_output={
            "key_issues": ["System access request"],
            "recommended_actions": ["Reset credentials"],
            "urgency_level": "Routine",
        },
    )
    assert approved.status == SummarisationStatus.APPROVED
    assert approved.advising_note is None


@pytest.mark.django_db
def test_validate_input_text_empty():
    with pytest.raises(Exception):
        validate_input_text("")


@pytest.mark.django_db
def test_validate_input_text_too_long():
    with pytest.raises(Exception):
        validate_input_text("x" * 5001)


@pytest.mark.django_db
@override_settings(AI_PROVIDER="deterministic")
def test_urgent_detection(advisor_user):
    result = create_summarisation_request(
        user=advisor_user,
        raw_text="Urgent: student has a family emergency and needs immediate extension on all deadlines.",
    )
    assert result.ai_output["urgency_level"] == "Urgent"
