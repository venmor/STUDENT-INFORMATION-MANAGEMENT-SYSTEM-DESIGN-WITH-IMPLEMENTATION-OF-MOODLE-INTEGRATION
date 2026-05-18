import pytest
from apps.accounts.constants import RoleCode
from apps.structure.models import Department, Programme, School, Stream
from apps.testutils import authenticated_client_for_user, create_user


@pytest.fixture
def admin_client(db):
    user = create_user(primary_role=RoleCode.ADMIN)
    return authenticated_client_for_user(user)


@pytest.fixture
def student_client(db):
    user = create_user(primary_role=RoleCode.STUDENT, username="struct_student")
    return authenticated_client_for_user(user)


@pytest.fixture
def school(db):
    return School.objects.create(code="SoNHAS", name="School of Natural and Health Applied Sciences")


@pytest.fixture
def department(school):
    return Department.objects.create(code="CS", name="Department of Computer Science", school=school)


@pytest.fixture
def programme(department):
    return Programme.objects.create(
        code="BSc-CS", name="Bachelor of Science in Computer Science",
        department=department, level="UG", duration_years=4,
    )


@pytest.fixture
def stream(programme):
    return Stream.objects.create(code="CS-SE", name="Software Engineering", programme=programme)


class TestSchoolAPI:
    def test_list_schools(self, admin_client, school):
        response = admin_client.get("/api/v1/structure/schools")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["code"] == "SoNHAS"

    def test_create_school_admin(self, admin_client):
        response = admin_client.post("/api/v1/structure/schools", {"code": "SoBE", "name": "Business"}, format="json")
        assert response.status_code == 201
        assert School.objects.filter(code="SoBE").exists()

    def test_create_school_denied_for_student(self, student_client):
        response = student_client.post("/api/v1/structure/schools", {"code": "X", "name": "X"}, format="json")
        assert response.status_code == 403

    def test_student_can_read_schools(self, student_client, school):
        response = student_client.get("/api/v1/structure/schools")
        assert response.status_code == 200


class TestDepartmentAPI:
    def test_list_departments(self, admin_client, department):
        response = admin_client.get("/api/v1/structure/departments")
        assert response.status_code == 200
        assert response.data[0]["school_name"] == "School of Natural and Health Applied Sciences"

    def test_filter_by_school(self, admin_client, department):
        response = admin_client.get(f"/api/v1/structure/departments?school={department.school_id}")
        assert response.status_code == 200
        assert len(response.data) == 1


class TestProgrammeAPI:
    def test_list_programmes(self, admin_client, programme):
        response = admin_client.get("/api/v1/structure/programmes")
        assert response.status_code == 200
        assert response.data[0]["department_name"] == "Department of Computer Science"

    def test_filter_by_level(self, admin_client, programme):
        response = admin_client.get("/api/v1/structure/programmes?level=UG")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_create_programme(self, admin_client, department):
        response = admin_client.post("/api/v1/structure/programmes", {
            "code": "MSc-CS", "name": "MSc Computer Science",
            "department": str(department.id), "level": "PG", "duration_years": 2,
        }, format="json")
        assert response.status_code == 201


class TestStreamAPI:
    def test_list_streams(self, admin_client, stream):
        response = admin_client.get("/api/v1/structure/streams")
        assert response.status_code == 200
        assert response.data[0]["programme_name"] == "Bachelor of Science in Computer Science"

    def test_filter_by_programme(self, admin_client, stream):
        response = admin_client.get(f"/api/v1/structure/streams?programme={stream.programme_id}")
        assert response.status_code == 200
        assert len(response.data) == 1
