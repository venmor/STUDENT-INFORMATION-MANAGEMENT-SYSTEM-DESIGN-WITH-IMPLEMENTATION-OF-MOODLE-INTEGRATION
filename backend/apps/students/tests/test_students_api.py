from apps.accounts.constants import AccessEventType, RoleCode
from apps.accounts.models import AccessLog
from apps.testutils import authenticate_client, create_user


def build_student_payload(user_id: int) -> dict:
    return {
        "user_id": user_id,
        "student_number": "S10001",
        "national_id": "NRC-10001",
        "date_of_birth": "2004-01-15",
        "gender": "Female",
        "programme": "BSc Computer Science",
        "year_of_study": 2,
    }


def test_admin_can_create_student_profile_and_assign_advisor(db):
    admin_user = create_user(
        username="student-admin",
        email="student-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Student Admin",
    )
    advisor_user = create_user(
        username="assigned-advisor",
        email="assigned-advisor@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADVISOR,
        full_name="Assigned Advisor",
    )
    student_user = create_user(
        username="student-record",
        email="student-record@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Student Record",
    )
    client = authenticate_client(username=admin_user.username, password="Secret123!")

    create_response = client.post("/api/v1/students", build_student_payload(student_user.id), format="json")
    assert create_response.status_code == 201, create_response.json()
    student_id = create_response.json()["id"]

    assignment_response = client.post(
        f"/api/v1/students/{student_id}/advisor-assignments",
        {"advisor_user_id": advisor_user.id, "effective_from": "2026-04-15"},
        format="json",
    )

    assert assignment_response.status_code == 201, assignment_response.json()


def test_student_detail_respects_self_and_advisor_visibility(db):
    admin_user = create_user(
        username="admin-detail",
        email="admin-detail@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Admin Detail",
    )
    advisor_user = create_user(
        username="advisor-detail",
        email="advisor-detail@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADVISOR,
        full_name="Advisor Detail",
    )
    stranger_advisor = create_user(
        username="advisor-stranger",
        email="advisor-stranger@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADVISOR,
        full_name="Stranger Advisor",
    )
    student_user = create_user(
        username="student-detail",
        email="student-detail@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Student Detail",
    )

    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    student_response = admin_client.post("/api/v1/students", build_student_payload(student_user.id), format="json")
    student_id = student_response.json()["id"]
    admin_client.post(
        f"/api/v1/students/{student_id}/advisor-assignments",
        {"advisor_user_id": advisor_user.id, "effective_from": "2026-04-15"},
        format="json",
    )

    advisor_client = authenticate_client(username=advisor_user.username, password="Secret123!")
    stranger_client = authenticate_client(username=stranger_advisor.username, password="Secret123!")
    student_client = authenticate_client(username=student_user.username, password="Secret123!")

    assert advisor_client.get(f"/api/v1/students/{student_id}").status_code == 200
    assert student_client.get(f"/api/v1/students/{student_id}").status_code == 200
    assert stranger_client.get(f"/api/v1/students/{student_id}").status_code == 403


def test_financial_flags_and_advising_note_workflow(db):
    admin_user = create_user(
        username="admin-flags",
        email="admin-flags@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Admin Flags",
    )
    advisor_user = create_user(
        username="advisor-flags",
        email="advisor-flags@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADVISOR,
        full_name="Advisor Flags",
    )
    student_user = create_user(
        username="student-flags",
        email="student-flags@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Student Flags",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    student_response = admin_client.post("/api/v1/students", build_student_payload(student_user.id), format="json")
    student_id = student_response.json()["id"]
    admin_client.post(
        f"/api/v1/students/{student_id}/advisor-assignments",
        {"advisor_user_id": advisor_user.id, "effective_from": "2026-04-15"},
        format="json",
    )

    flag_response = admin_client.post(
        f"/api/v1/students/{student_id}/financial-flags",
        {
            "flag_type": "financial_hold",
            "reason": "Outstanding tuition",
            "effective_date": "2026-04-15",
        },
        format="json",
    )
    assert flag_response.status_code == 201, flag_response.json()

    advisor_client = authenticate_client(username=advisor_user.username, password="Secret123!")
    note_response = advisor_client.post(
        f"/api/v1/students/{student_id}/advising-notes",
        {"note_text": "Student needs a payment plan review."},
        format="json",
    )
    assert note_response.status_code == 201, note_response.json()
    note_id = note_response.json()["id"]

    approve_response = admin_client.post(
        f"/api/v1/students/{student_id}/advising-notes/{note_id}/approve",
        format="json",
    )
    assert approve_response.status_code == 200, approve_response.json()

    list_response = advisor_client.get(f"/api/v1/students/{student_id}/financial-flags")
    assert list_response.status_code == 200, list_response.json()
    assert list_response.json()[0]["flag_type"] == "financial_hold"


def test_admin_can_soft_deactivate_student_and_exclude_from_active_list(db):
    admin_user = create_user(
        username="admin-deactivate-student",
        email="admin-deactivate-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Admin Deactivate Student",
    )
    student_user = create_user(
        username="student-deactivate",
        email="student-deactivate@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Student Deactivate",
    )

    client = authenticate_client(username=admin_user.username, password="Secret123!")
    create_response = client.post("/api/v1/students", build_student_payload(student_user.id), format="json")
    student_id = create_response.json()["id"]

    deactivate_response = client.post(f"/api/v1/students/{student_id}/deactivate", format="json")

    assert deactivate_response.status_code == 200, deactivate_response.json()
    assert deactivate_response.json()["detail"] == "Student record deactivated."

    list_response = client.get("/api/v1/students")
    assert list_response.status_code == 200, list_response.json()
    assert all(student["id"] != student_id for student in list_response.json())

    detail_response = client.get(f"/api/v1/students/{student_id}")
    assert detail_response.status_code == 200, detail_response.json()
    assert detail_response.json()["is_active"] is False


def test_student_update_logs_field_level_changes_and_read_events(db):
    admin_user = create_user(
        username="admin-student-audit",
        email="admin-student-audit@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Admin Student Audit",
    )
    student_user = create_user(
        username="student-audit",
        email="student-audit@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Student Audit",
    )

    client = authenticate_client(username=admin_user.username, password="Secret123!")
    create_response = client.post("/api/v1/students", build_student_payload(student_user.id), format="json")
    student_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/students/{student_id}",
        {"programme": "BSc Information Systems", "year_of_study": 3},
        format="json",
    )
    assert update_response.status_code == 200, update_response.json()

    list_response = client.get("/api/v1/students")
    assert list_response.status_code == 200, list_response.json()

    update_log = AccessLog.objects.filter(
        event_type=AccessEventType.API_ACTION,
        view_name="student-detail",
        metadata__action="update",
    ).latest("created_at")

    assert update_log.metadata["changes"] == {
        "programme": {"before": "BSc Computer Science", "after": "BSc Information Systems"},
        "year_of_study": {"before": 2, "after": 3},
    }

    list_log = AccessLog.objects.filter(
        event_type=AccessEventType.API_ACTION,
        view_name="students-list-create",
        metadata__action="read_list",
    ).latest("created_at")

    assert list_log.metadata["student_count"] == 1
    assert student_id in list_log.metadata["student_ids"]
