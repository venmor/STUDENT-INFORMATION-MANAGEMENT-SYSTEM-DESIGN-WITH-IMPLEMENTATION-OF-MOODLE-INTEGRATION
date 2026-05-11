from apps.accounts.constants import RoleCode
from apps.testutils import authenticate_client, create_user


def create_student_profile(admin_client, student_user_id: int, student_number: str):
    response = admin_client.post(
        "/api/v1/students",
        {
            "user_id": student_user_id,
            "student_number": student_number,
            "national_id": f"NRC-{student_number}",
            "date_of_birth": "2004-01-15",
            "gender": "Female",
            "programme": "BSc Computer Science",
            "year_of_study": 2,
        },
        format="json",
    )
    assert response.status_code == 201, response.json()
    return response.json()


def create_course_and_section(admin_client, faculty_user_id: int, *, course_code: str):
    course_response = admin_client.post(
        "/api/v1/courses",
        {
            "course_code": course_code,
            "course_title": f"{course_code} Title",
            "department": "Computer Science",
            "credit_hours": 3,
            "description": "Gradeable course.",
            "programme_code": "BSc Computer Science",
            "max_capacity": 50,
        },
        format="json",
    )
    section_response = admin_client.post(
        "/api/v1/sections",
        {
            "course_id": course_response.json()["id"],
            "section_code": "A",
            "faculty_user_id": faculty_user_id,
            "room": "Hall 1",
            "semester": "Semester 1",
            "academic_year": "2026/2027",
            "max_capacity": 50,
            "registration_opens_at": "2026-04-01T00:00:00Z",
            "registration_closes_at": "2026-05-01T23:59:59Z",
            "drop_deadline": "2026-05-15T23:59:59Z",
            "timetables": [
                {"day_of_week": "Tuesday", "start_time": "10:00:00", "end_time": "12:00:00"}
            ],
        },
        format="json",
    )
    return course_response.json(), section_response.json()


def test_faculty_can_enter_draft_grade_and_admin_can_officialise_it(db):
    admin_user = create_user(
        username="grade-admin",
        email="grade-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Grade Admin",
    )
    faculty_user = create_user(
        username="grade-faculty",
        email="grade-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Grade Faculty",
    )
    student_user = create_user(
        username="grade-student",
        email="grade-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Grade Student",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    faculty_client = authenticate_client(username=faculty_user.username, password="Secret123!")

    create_student_profile(admin_client, student_user.id, "S50001")
    _, section_body = create_course_and_section(admin_client, faculty_user.id, course_code="CSC301")
    enrollment_response = admin_client.post(
        "/api/v1/enrollments",
        {"student_user_id": student_user.id, "section_id": section_body["id"]},
        format="json",
    )
    assert enrollment_response.status_code == 201, enrollment_response.json()

    draft_response = faculty_client.post(
        "/api/v1/grades",
        {
            "student_user_id": student_user.id,
            "section_id": section_body["id"],
            "numeric_score": "86.0",
        },
        format="json",
    )
    assert draft_response.status_code == 201, draft_response.json()
    assert draft_response.json()["grade_status"] == "DRAFT"

    official_response = admin_client.post(
        f"/api/v1/grades/{draft_response.json()['id']}/officialise",
        format="json",
    )
    assert official_response.status_code == 200, official_response.json()
    assert official_response.json()["grade_status"] == "OFFICIAL"


def test_official_grade_updates_gpa_and_transcript_pdf(db):
    admin_user = create_user(
        username="gpa-admin",
        email="gpa-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="GPA Admin",
    )
    faculty_user = create_user(
        username="gpa-faculty",
        email="gpa-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="GPA Faculty",
    )
    student_user = create_user(
        username="gpa-student",
        email="gpa-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="GPA Student",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    faculty_client = authenticate_client(username=faculty_user.username, password="Secret123!")
    student_profile = create_student_profile(admin_client, student_user.id, "S50002")

    _, section_body = create_course_and_section(admin_client, faculty_user.id, course_code="CSC302")
    admin_client.post(
        "/api/v1/enrollments",
        {"student_user_id": student_user.id, "section_id": section_body["id"]},
        format="json",
    )

    draft_response = faculty_client.post(
        "/api/v1/grades",
        {
            "student_user_id": student_user.id,
            "section_id": section_body["id"],
            "numeric_score": "92.0",
        },
        format="json",
    )
    admin_client.post(
        f"/api/v1/grades/{draft_response.json()['id']}/officialise",
        format="json",
    )

    profile_response = admin_client.get(f"/api/v1/students/{student_profile['id']}")
    assert profile_response.status_code == 200, profile_response.json()
    assert profile_response.json()["cumulative_gpa"] == "4.00"

    transcript_response = admin_client.get(f"/api/v1/students/{student_profile['id']}/transcript")
    assert transcript_response.status_code == 200
    assert transcript_response["Content-Type"] == "application/pdf"


def test_official_grade_change_requires_reason(db):
    admin_user = create_user(
        username="gradechange-admin",
        email="gradechange-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Grade Change Admin",
    )
    faculty_user = create_user(
        username="gradechange-faculty",
        email="gradechange-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Grade Change Faculty",
    )
    student_user = create_user(
        username="gradechange-student",
        email="gradechange-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Grade Change Student",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    faculty_client = authenticate_client(username=faculty_user.username, password="Secret123!")
    create_student_profile(admin_client, student_user.id, "S50003")

    _, section_body = create_course_and_section(admin_client, faculty_user.id, course_code="CSC303")
    admin_client.post(
        "/api/v1/enrollments",
        {"student_user_id": student_user.id, "section_id": section_body["id"]},
        format="json",
    )
    draft_response = faculty_client.post(
        "/api/v1/grades",
        {
            "student_user_id": student_user.id,
            "section_id": section_body["id"],
            "numeric_score": "80.0",
        },
        format="json",
    )
    admin_client.post(
        f"/api/v1/grades/{draft_response.json()['id']}/officialise",
        format="json",
    )

    missing_reason_response = admin_client.patch(
        f"/api/v1/grades/{draft_response.json()['id']}",
        {"numeric_score": "84.0"},
        format="json",
    )
    assert missing_reason_response.status_code == 400

    reason_response = admin_client.patch(
        f"/api/v1/grades/{draft_response.json()['id']}",
        {"numeric_score": "84.0", "change_reason": "Approved moderation correction"},
        format="json",
    )
    assert reason_response.status_code == 200, reason_response.json()


def test_grade_create_and_update_require_active_enrollment(db):
    admin_user = create_user(
        username="grade-enrollment-admin",
        email="grade-enrollment-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Grade Enrollment Admin",
    )
    faculty_user = create_user(
        username="grade-enrollment-faculty",
        email="grade-enrollment-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Grade Enrollment Faculty",
    )
    student_user = create_user(
        username="grade-enrollment-student",
        email="grade-enrollment-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Grade Enrollment Student",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    faculty_client = authenticate_client(username=faculty_user.username, password="Secret123!")

    create_student_profile(admin_client, student_user.id, "S50004")
    _, section_body = create_course_and_section(admin_client, faculty_user.id, course_code="CSC304")

    not_enrolled_response = faculty_client.post(
        "/api/v1/grades",
        {
            "student_user_id": student_user.id,
            "section_id": section_body["id"],
            "numeric_score": "74.0",
        },
        format="json",
    )
    assert not_enrolled_response.status_code == 400

    enrollment_response = admin_client.post(
        "/api/v1/enrollments",
        {"student_user_id": student_user.id, "section_id": section_body["id"]},
        format="json",
    )
    assert enrollment_response.status_code == 201, enrollment_response.json()

    draft_response = faculty_client.post(
        "/api/v1/grades",
        {
            "student_user_id": student_user.id,
            "section_id": section_body["id"],
            "numeric_score": "74.0",
        },
        format="json",
    )
    assert draft_response.status_code == 201, draft_response.json()

    drop_response = admin_client.post(
        f"/api/v1/enrollments/{enrollment_response.json()['id']}/drop",
        {"reason": "Late schedule correction"},
        format="json",
    )
    assert drop_response.status_code == 200, drop_response.json()

    update_response = admin_client.patch(
        f"/api/v1/grades/{draft_response.json()['id']}",
        {"numeric_score": "79.0"},
        format="json",
    )
    assert update_response.status_code == 400


def test_grade_list_respects_role_visibility(db):
    admin_user = create_user(
        username="grade-list-admin",
        email="grade-list-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Grade List Admin",
    )
    faculty_user = create_user(
        username="grade-list-faculty",
        email="grade-list-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Grade List Faculty",
    )
    advisor_user = create_user(
        username="grade-list-advisor",
        email="grade-list-advisor@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADVISOR,
        full_name="Grade List Advisor",
    )
    student_user = create_user(
        username="grade-list-student",
        email="grade-list-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Grade List Student",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    faculty_client = authenticate_client(username=faculty_user.username, password="Secret123!")
    advisor_client = authenticate_client(username=advisor_user.username, password="Secret123!")
    student_client = authenticate_client(username=student_user.username, password="Secret123!")

    student_profile = create_student_profile(admin_client, student_user.id, "S50005")
    assignment_response = admin_client.post(
        f"/api/v1/students/{student_profile['id']}/advisor-assignments",
        {"advisor_user_id": advisor_user.id, "effective_from": "2026-04-15"},
        format="json",
    )
    assert assignment_response.status_code == 201, assignment_response.json()

    _, official_section = create_course_and_section(admin_client, faculty_user.id, course_code="CSC305")
    _, draft_section = create_course_and_section(admin_client, faculty_user.id, course_code="CSC306")

    for section_id in (official_section["id"], draft_section["id"]):
        enrollment_response = admin_client.post(
            "/api/v1/enrollments",
            {"student_user_id": student_user.id, "section_id": section_id},
            format="json",
        )
        assert enrollment_response.status_code == 201, enrollment_response.json()

    official_grade_response = faculty_client.post(
        "/api/v1/grades",
        {
            "student_user_id": student_user.id,
            "section_id": official_section["id"],
            "numeric_score": "91.0",
        },
        format="json",
    )
    assert official_grade_response.status_code == 201, official_grade_response.json()
    officialise_response = admin_client.post(
        f"/api/v1/grades/{official_grade_response.json()['id']}/officialise",
        format="json",
    )
    assert officialise_response.status_code == 200, officialise_response.json()

    draft_grade_response = faculty_client.post(
        "/api/v1/grades",
        {
            "student_user_id": student_user.id,
            "section_id": draft_section["id"],
            "numeric_score": "67.0",
        },
        format="json",
    )
    assert draft_grade_response.status_code == 201, draft_grade_response.json()

    student_grade_list_response = student_client.get("/api/v1/grades")
    assert student_grade_list_response.status_code == 200, student_grade_list_response.json()
    assert len(student_grade_list_response.json()) == 1
    assert student_grade_list_response.json()[0]["grade_status"] == "OFFICIAL"

    advisor_grade_list_response = advisor_client.get(f"/api/v1/grades?student_id={student_profile['id']}")
    assert advisor_grade_list_response.status_code == 200, advisor_grade_list_response.json()
    assert len(advisor_grade_list_response.json()) == 1
    assert advisor_grade_list_response.json()[0]["course_code"] == "CSC305"

    faculty_grade_list_response = faculty_client.get("/api/v1/grades")
    assert faculty_grade_list_response.status_code == 200, faculty_grade_list_response.json()
    assert len(faculty_grade_list_response.json()) == 2

    admin_grade_list_response = admin_client.get(f"/api/v1/grades?student_id={student_profile['id']}")
    assert admin_grade_list_response.status_code == 200, admin_grade_list_response.json()
    assert len(admin_grade_list_response.json()) == 2
