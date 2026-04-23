from django.core.files.uploadedfile import SimpleUploadedFile

from apps.accounts.constants import RoleCode
from apps.testutils import authenticate_client, create_user


def create_student_profile(admin_client, student_user_id: int, *, student_number: str, programme: str = "BSc Computer Science"):
    response = admin_client.post(
        "/api/v1/students",
        {
            "user_id": student_user_id,
            "student_number": student_number,
            "national_id": f"NRC-{student_number}",
            "date_of_birth": "2004-01-15",
            "gender": "Female",
            "programme": programme,
            "year_of_study": 2,
        },
        format="json",
    )
    assert response.status_code == 201, response.json()
    return response.json()


def create_course_and_section(admin_client, faculty_user_id: int, *, course_code: str = "CSC201"):
    course_response = admin_client.post(
        "/api/v1/courses",
        {
            "course_code": course_code,
            "course_title": f"{course_code} Title",
            "department": "Computer Science",
            "credit_hours": 3,
            "description": "Core algorithms and data structures.",
            "programme_code": "BSc Computer Science",
            "max_capacity": 1,
        },
        format="json",
    )
    assert course_response.status_code == 201, course_response.json()
    course_id = course_response.json()["id"]

    section_response = admin_client.post(
        "/api/v1/sections",
        {
            "course_id": course_id,
            "section_code": "A",
            "faculty_user_id": faculty_user_id,
            "room": "Lab 2",
            "semester": "Semester 1",
            "academic_year": "2026/2027",
            "max_capacity": 1,
            "registration_opens_at": "2026-04-01T00:00:00Z",
            "registration_closes_at": "2026-05-01T23:59:59Z",
            "drop_deadline": "2026-05-15T23:59:59Z",
            "timetables": [
                {"day_of_week": "Monday", "start_time": "09:00:00", "end_time": "11:00:00"}
            ],
        },
        format="json",
    )
    assert section_response.status_code == 201, section_response.json()
    return course_response.json(), section_response.json()


def test_admin_can_create_course_section_and_timetable(db):
    admin_user = create_user(
        username="courses-admin",
        email="courses-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Courses Admin",
    )
    faculty_user = create_user(
        username="faculty-course",
        email="faculty-course@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Faculty Course",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")

    course_body, section_body = create_course_and_section(admin_client, faculty_user.id)

    assert course_body["course_code"] == "CSC201"
    assert section_body["timetables"][0]["day_of_week"] == "Monday"


def test_self_enrollment_enforces_prerequisites_and_waitlist(db):
    admin_user = create_user(
        username="enroll-admin",
        email="enroll-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Enroll Admin",
    )
    faculty_user = create_user(
        username="enroll-faculty",
        email="enroll-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Enroll Faculty",
    )
    first_student_user = create_user(
        username="first-student",
        email="first-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="First Student",
    )
    second_student_user = create_user(
        username="second-student",
        email="second-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Second Student",
    )
    prerequisite_student_user = create_user(
        username="prereq-student",
        email="prereq-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Prereq Student",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")

    create_student_profile(admin_client, first_student_user.id, student_number="S20001")
    create_student_profile(admin_client, second_student_user.id, student_number="S20002")
    create_student_profile(admin_client, prerequisite_student_user.id, student_number="S20003")

    prerequisite_course_response = admin_client.post(
        "/api/v1/courses",
        {
            "course_code": "CSC101",
            "course_title": "Introduction to Computing",
            "department": "Computer Science",
            "credit_hours": 3,
            "description": "Foundations.",
            "programme_code": "BSc Computer Science",
            "max_capacity": 50,
        },
        format="json",
    )
    course_body, section_body = create_course_and_section(admin_client, faculty_user.id)
    prereq_link = admin_client.post(
        f"/api/v1/courses/{course_body['id']}/prerequisites",
        {"prerequisite_course_id": prerequisite_course_response.json()["id"]},
        format="json",
    )
    assert prereq_link.status_code == 201, prereq_link.json()

    prereq_student_client = authenticate_client(username=prerequisite_student_user.username, password="Secret123!")
    blocked_response = prereq_student_client.post(
        "/api/v1/enrollments",
        {"section_id": section_body["id"]},
        format="json",
    )
    assert blocked_response.status_code == 400

    _, open_section = create_course_and_section(admin_client, faculty_user.id, course_code="CSC202")

    admin_enroll = admin_client.post(
        "/api/v1/enrollments",
        {"student_user_id": first_student_user.id, "section_id": open_section["id"]},
        format="json",
    )
    assert admin_enroll.status_code == 201, admin_enroll.json()

    second_student_client = authenticate_client(username=second_student_user.username, password="Secret123!")
    waitlist_response = second_student_client.post(
        "/api/v1/enrollments",
        {"section_id": open_section["id"], "waitlist_if_full": True},
        format="json",
    )
    assert waitlist_response.status_code == 201, waitlist_response.json()
    assert waitlist_response.json()["enrollment_status"] == "WAITLISTED"


def test_bulk_enrollment_preview_and_commit(db):
    admin_user = create_user(
        username="bulk-admin",
        email="bulk-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Bulk Admin",
    )
    faculty_user = create_user(
        username="bulk-faculty",
        email="bulk-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Bulk Faculty",
    )
    student_user = create_user(
        username="bulk-student",
        email="bulk-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Bulk Student",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    student_profile = create_student_profile(admin_client, student_user.id, student_number="S30001")
    _, section_body = create_course_and_section(admin_client, faculty_user.id)

    preview_file = SimpleUploadedFile(
        "enrollments.csv",
        f"student_id,section_id\n{student_profile['id']},{section_body['id']}\ninvalid,{section_body['id']}\n".encode(),
        content_type="text/csv",
    )
    preview_response = admin_client.post(
        "/api/v1/enrollments/bulk-preview",
        {"file": preview_file},
    )
    assert preview_response.status_code == 200, preview_response.json()
    assert preview_response.json()["error_count"] == 1

    commit_file = SimpleUploadedFile(
        "enrollments.csv",
        f"student_id,section_id\n{student_profile['id']},{section_body['id']}\n".encode(),
        content_type="text/csv",
    )
    commit_response = admin_client.post(
        "/api/v1/enrollments/bulk-commit",
        {"file": commit_file},
    )

    assert commit_response.status_code == 201, commit_response.json()
    assert commit_response.json()["created_count"] == 1


def test_transfer_moves_enrollment_to_target_section(db):
    admin_user = create_user(
        username="transfer-admin",
        email="transfer-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Transfer Admin",
    )
    faculty_user = create_user(
        username="transfer-faculty",
        email="transfer-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Transfer Faculty",
    )
    student_user = create_user(
        username="transfer-student",
        email="transfer-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Transfer Student",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    create_student_profile(admin_client, student_user.id, student_number="S40001")
    _, source_section = create_course_and_section(admin_client, faculty_user.id, course_code="CSC401")
    _, target_section = create_course_and_section(admin_client, faculty_user.id, course_code="CSC402")

    enroll_response = admin_client.post(
        "/api/v1/enrollments",
        {"student_user_id": student_user.id, "section_id": source_section["id"]},
        format="json",
    )
    enrollment_id = enroll_response.json()["id"]

    transfer_response = admin_client.post(
        f"/api/v1/enrollments/{enrollment_id}/transfer",
        {"target_section_id": target_section["id"]},
        format="json",
    )

    assert transfer_response.status_code == 200, transfer_response.json()
    assert transfer_response.json()["section"]["id"] == target_section["id"]


def test_section_reads_and_roster_follow_role_scope(db):
    admin_user = create_user(
        username="section-read-admin",
        email="section-read-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Section Read Admin",
    )
    faculty_user = create_user(
        username="section-read-faculty",
        email="section-read-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Section Read Faculty",
    )
    other_faculty_user = create_user(
        username="section-read-other-faculty",
        email="section-read-other-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Other Faculty",
    )
    student_user = create_user(
        username="section-read-student",
        email="section-read-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Section Read Student",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    faculty_client = authenticate_client(username=faculty_user.username, password="Secret123!")
    other_faculty_client = authenticate_client(username=other_faculty_user.username, password="Secret123!")
    student_client = authenticate_client(username=student_user.username, password="Secret123!")

    student_profile = create_student_profile(admin_client, student_user.id, student_number="S45001")
    _, section_body = create_course_and_section(admin_client, faculty_user.id, course_code="CSC450")
    enrollment_response = admin_client.post(
        "/api/v1/enrollments",
        {"student_user_id": student_user.id, "section_id": section_body["id"]},
        format="json",
    )
    assert enrollment_response.status_code == 201, enrollment_response.json()

    faculty_sections_response = faculty_client.get("/api/v1/sections")
    assert faculty_sections_response.status_code == 200, faculty_sections_response.json()
    assert [section["id"] for section in faculty_sections_response.json()] == [section_body["id"]]

    student_sections_response = student_client.get("/api/v1/sections")
    assert student_sections_response.status_code == 200, student_sections_response.json()
    assert section_body["id"] in [section["id"] for section in student_sections_response.json()]

    admin_roster_response = admin_client.get(f"/api/v1/sections/{section_body['id']}/roster")
    assert admin_roster_response.status_code == 200, admin_roster_response.json()
    assert admin_roster_response.json()[0]["student_number"] == student_profile["student_number"]

    faculty_roster_response = faculty_client.get(f"/api/v1/sections/{section_body['id']}/roster")
    assert faculty_roster_response.status_code == 200, faculty_roster_response.json()
    assert faculty_roster_response.json()[0]["student_number"] == student_profile["student_number"]

    other_faculty_roster_response = other_faculty_client.get(f"/api/v1/sections/{section_body['id']}/roster")
    assert other_faculty_roster_response.status_code == 403


def test_student_cannot_bypass_programme_filter_on_course_or_section_detail(db):
    admin_user = create_user(
        username="programme-filter-admin",
        email="programme-filter-admin@example.com",
        password="Secret123!",
        primary_role=RoleCode.ADMIN,
        full_name="Programme Filter Admin",
    )
    faculty_user = create_user(
        username="programme-filter-faculty",
        email="programme-filter-faculty@example.com",
        password="Secret123!",
        primary_role=RoleCode.FACULTY,
        full_name="Programme Filter Faculty",
    )
    student_user = create_user(
        username="programme-filter-student",
        email="programme-filter-student@example.com",
        password="Secret123!",
        primary_role=RoleCode.STUDENT,
        full_name="Programme Filter Student",
    )
    admin_client = authenticate_client(username=admin_user.username, password="Secret123!")
    student_client = authenticate_client(username=student_user.username, password="Secret123!")

    create_student_profile(admin_client, student_user.id, student_number="S45002", programme="BSc Computer Science")

    hidden_course_response = admin_client.post(
        "/api/v1/courses",
        {
            "course_code": "HIS201",
            "course_title": "History of Ideas",
            "department": "History",
            "credit_hours": 3,
            "description": "Off-programme course.",
            "programme_code": "BA History",
            "max_capacity": 30,
        },
        format="json",
    )
    assert hidden_course_response.status_code == 201, hidden_course_response.json()
    hidden_course_id = hidden_course_response.json()["id"]

    hidden_section_response = admin_client.post(
        "/api/v1/sections",
        {
            "course_id": hidden_course_id,
            "section_code": "A",
            "faculty_user_id": faculty_user.id,
            "room": "Hall 2",
            "semester": "Semester 1",
            "academic_year": "2026/2027",
            "max_capacity": 30,
            "registration_opens_at": "2026-04-01T00:00:00Z",
            "registration_closes_at": "2026-05-01T23:59:59Z",
            "drop_deadline": "2026-05-15T23:59:59Z",
            "timetables": [
                {"day_of_week": "Wednesday", "start_time": "13:00:00", "end_time": "15:00:00"}
            ],
        },
        format="json",
    )
    assert hidden_section_response.status_code == 201, hidden_section_response.json()

    hidden_course_detail_response = student_client.get(f"/api/v1/courses/{hidden_course_id}")
    assert hidden_course_detail_response.status_code == 404

    hidden_section_detail_response = student_client.get(
        f"/api/v1/sections/{hidden_section_response.json()['id']}"
    )
    assert hidden_section_detail_response.status_code == 404
