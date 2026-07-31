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


def create_course_and_section(admin_client, faculty_user_id: int, *, course_code: str = "CSC901") -> tuple[dict, dict]:
    course_response = admin_client.post(
        "/api/v1/courses",
        {
            "course_code": course_code,
            "course_title": f"{course_code} Title",
            "department": "Computer Science",
            "credit_hours": 3,
            "description": "Profile-linked course.",
            "programme_code": "BSc Computer Science",
            "max_capacity": 50,
        },
        format="json",
    )
    assert course_response.status_code == 201, course_response.json()

    section_response = admin_client.post(
        "/api/v1/sections",
        {
            "course_id": course_response.json()["id"],
            "section_code": "A",
            "faculty_user_id": faculty_user_id,
            "room": "Hall 4",
            "semester": "Semester 1",
            "academic_year": "2026/2027",
            "max_capacity": 50,
            "registration_opens_at": "2026-04-01T00:00:00Z",
            "registration_closes_at": "2026-05-01T23:59:59Z",
            "drop_deadline": "2026-05-15T23:59:59Z",
            "timetables": [
                {"day_of_week": "Thursday", "start_time": "10:00:00", "end_time": "12:00:00"}
            ],
        },
        format="json",
    )
    assert section_response.status_code == 201, section_response.json()
    return course_response.json(), section_response.json()


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


def test_financial_flag_update_and_clear_flow(db):
    admin_user = create_user(
        username="admin-flag-update",
        email="admin-flag-update@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Admin Flag Update",
    )
    student_user = create_user(
        username="student-flag-update",
        email="student-flag-update@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Student Flag Update",
    )

    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    student_response = admin_client.post("/api/v1/students", build_student_payload(student_user.id), format="json")
    student_id = student_response.json()["id"]

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
    flag_id = flag_response.json()["id"]

    update_response = admin_client.patch(
        f"/api/v1/students/{student_id}/financial-flags/{flag_id}",
        {"reason": "Outstanding tuition balance after review"},
        format="json",
    )
    assert update_response.status_code == 200, update_response.json()
    assert update_response.json()["reason"] == "Outstanding tuition balance after review"

    clear_response = admin_client.patch(
        f"/api/v1/students/{student_id}/financial-flags/{flag_id}",
        {"cleared_date": "2026-04-20"},
        format="json",
    )
    assert clear_response.status_code == 200, clear_response.json()
    assert clear_response.json()["cleared_date"] == "2026-04-20"


def test_advising_note_update_is_audited_and_blocks_approved_edits(db):
    admin_user = create_user(
        username="admin-note-update",
        email="admin-note-update@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Admin Note Update",
    )
    advisor_user = create_user(
        username="advisor-note-update",
        email="advisor-note-update@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADVISOR,
        full_name="Advisor Note Update",
    )
    student_user = create_user(
        username="student-note-update",
        email="student-note-update@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Student Note Update",
    )

    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    advisor_client = authenticate_client(username=advisor_user.username, password="Secret123!")
    student_response = admin_client.post("/api/v1/students", build_student_payload(student_user.id), format="json")
    student_id = student_response.json()["id"]
    assignment_response = admin_client.post(
        f"/api/v1/students/{student_id}/advisor-assignments",
        {"advisor_user_id": advisor_user.id, "effective_from": "2026-04-15"},
        format="json",
    )
    assert assignment_response.status_code == 201, assignment_response.json()

    note_response = advisor_client.post(
        f"/api/v1/students/{student_id}/advising-notes",
        {"note_text": "Initial draft note."},
        format="json",
    )
    assert note_response.status_code == 201, note_response.json()
    note_id = note_response.json()["id"]

    update_response = advisor_client.patch(
        f"/api/v1/students/{student_id}/advising-notes/{note_id}",
        {"note_text": "Updated draft note."},
        format="json",
    )
    assert update_response.status_code == 200, update_response.json()
    assert update_response.json()["note_text"] == "Updated draft note."

    update_log = AccessLog.objects.filter(
        event_type=AccessEventType.API_ACTION,
        view_name="student-advising-note-detail",
        metadata__action="update",
    ).latest("created_at")
    assert update_log.metadata["changes"] == {
        "note_text": {"before": "Initial draft note.", "after": "Updated draft note."},
    }

    approve_response = admin_client.post(
        f"/api/v1/students/{student_id}/advising-notes/{note_id}/approve",
        format="json",
    )
    assert approve_response.status_code == 200, approve_response.json()

    approved_update_response = advisor_client.patch(
        f"/api/v1/students/{student_id}/advising-notes/{note_id}",
        {"note_text": "Should not update approved note."},
        format="json",
    )
    assert approved_update_response.status_code == 400


def test_student_detail_exposes_attendance_percentages_and_requires_standing_override_reason(db):
    admin_user = create_user(
        username="admin-attendance-detail",
        email="admin-attendance-detail@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Admin Attendance Detail",
    )
    faculty_user = create_user(
        username="faculty-attendance-detail",
        email="faculty-attendance-detail@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Faculty Attendance Detail",
    )
    student_user = create_user(
        username="student-attendance-detail",
        email="student-attendance-detail@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Student Attendance Detail",
    )

    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    faculty_client = authenticate_client(username=faculty_user.username, password="Secret123!")
    student_response = admin_client.post("/api/v1/students", build_student_payload(student_user.id), format="json")
    student_id = student_response.json()["id"]
    _, section_body = create_course_and_section(admin_client, faculty_user.id)
    enrollment_response = admin_client.post(
        "/api/v1/enrollments",
        {"student_user_id": student_user.id, "section_id": section_body["id"]},
        format="json",
    )
    assert enrollment_response.status_code == 201, enrollment_response.json()

    first_attendance_response = faculty_client.post(
        "/api/v1/attendance/sessions",
        {
            "section_id": section_body["id"],
            "session_date": "2026-04-18",
            "records": [{"student_id": student_id, "status": "PRESENT"}],
        },
        format="json",
    )
    assert first_attendance_response.status_code == 201, first_attendance_response.json()

    second_attendance_response = faculty_client.post(
        "/api/v1/attendance/sessions",
        {
            "section_id": section_body["id"],
            "session_date": "2026-04-19",
            "records": [{"student_id": student_id, "status": "ABSENT"}],
        },
        format="json",
    )
    assert second_attendance_response.status_code == 201, second_attendance_response.json()

    detail_response = admin_client.get(f"/api/v1/students/{student_id}")
    assert detail_response.status_code == 200, detail_response.json()
    assert detail_response.json()["attendance_percentages"] == [
        {
            "section_id": section_body["id"],
            "course_code": "CSC901",
            "attendance_percentage": "50.00",
            "threshold": "75.00",
        }
    ]

    missing_reason_response = admin_client.patch(
        f"/api/v1/students/{student_id}",
        {"academic_standing": "PROBATION"},
        format="json",
    )
    assert missing_reason_response.status_code == 400

    override_response = admin_client.patch(
        f"/api/v1/students/{student_id}",
        {
            "academic_standing": "PROBATION",
            "standing_override_reason": "Manual registrar review after appeal",
        },
        format="json",
    )
    assert override_response.status_code == 200, override_response.json()


def test_student_correction_request_workflow(db):
    admin_user = create_user(
        username="admin-correction-request",
        email="admin-correction-request@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Admin Correction Request",
    )
    student_user = create_user(
        username="student-correction-request",
        email="student-correction-request@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Student Correction Request",
    )

    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    student_client = authenticate_client(username=student_user.username, password="Secret123!")
    student_response = admin_client.post("/api/v1/students", build_student_payload(student_user.id), format="json")
    student_id = student_response.json()["id"]

    create_request_response = student_client.post(
        f"/api/v1/students/{student_id}/correction-requests",
        {
            "requested_changes": {"national_id": "NRC-10001-CORRECTED"},
            "justification": "National registration card was entered incorrectly.",
        },
        format="json",
    )
    assert create_request_response.status_code == 201, create_request_response.json()
    correction_request_id = create_request_response.json()["id"]
    assert create_request_response.json()["status"] == "PENDING"

    student_list_response = student_client.get(f"/api/v1/students/{student_id}/correction-requests")
    assert student_list_response.status_code == 200, student_list_response.json()
    assert len(student_list_response.json()) == 1

    review_response = admin_client.patch(
        f"/api/v1/students/{student_id}/correction-requests/{correction_request_id}",
        {"status": "APPROVED", "review_note": "Approved for registrar follow-up."},
        format="json",
    )
    assert review_response.status_code == 200, review_response.json()
    assert review_response.json()["status"] == "APPROVED"
    assert review_response.json()["review_note"] == "Approved for registrar follow-up."


def test_advisor_cannot_create_student_profile_even_with_invalid_data(db):
    """
    Security test to ensure that the role check happens before validation (fail-fast).
    """
    advisor_user = create_user(
        username="unauthorized-advisor",
        email="unauthorized-advisor@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADVISOR,
        full_name="Unauthorized Advisor",
    )
    client = authenticate_client(username=advisor_user.username, password="Secret123!")

    # Attempt to create with empty data.
    # If the role check is first, it should return 403 Forbidden.
    # If validation happens first, it might return 400 Bad Request.
    response = client.post("/api/v1/students", {}, format="json")
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access is required."
