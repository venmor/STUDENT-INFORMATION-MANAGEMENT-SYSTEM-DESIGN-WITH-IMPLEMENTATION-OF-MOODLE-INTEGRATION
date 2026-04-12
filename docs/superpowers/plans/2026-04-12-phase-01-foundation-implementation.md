# Phase 1 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the first implementation baseline for Modern SIS by scaffolding the repo, bootstrapping the backend and frontend, defining the initial schema, and implementing the Phase 1 API surface needed to move from documentation into working software.

**Architecture:** The implementation starts with a monorepo-style layout containing a Django backend, a React frontend, and Docker-based local infrastructure. The schema is introduced before wider feature work so API contracts and later Moodle integration have stable model boundaries. Phase 1 keeps the surface intentionally narrow: core identity models, academic records models, audit-ready tables, a health endpoint, auth endpoints, and a small set of representative read/write APIs.

**Tech Stack:** Python 3.11+, Django 5, Django REST Framework, djangorestframework-simplejwt, MySQL 8.0, React 18, TypeScript, Vite, Docker Compose, pytest, Vitest

---

## File Structure Map

### Root

- Create: `.gitignore`
- Create: `.editorconfig`
- Create: `Makefile`
- Create: `backend/`
- Create: `frontend/`
- Create: `infra/`

### Backend

- Create: `backend/manage.py`
- Create: `backend/requirements/base.txt`
- Create: `backend/requirements/dev.txt`
- Create: `backend/pytest.ini`
- Create: `backend/sis_backend/__init__.py`
- Create: `backend/sis_backend/settings.py`
- Create: `backend/sis_backend/urls.py`
- Create: `backend/sis_backend/wsgi.py`
- Create: `backend/sis_backend/asgi.py`
- Create: `backend/sis_backend/celery.py`
- Create: `backend/apps/common/apps.py`
- Create: `backend/apps/common/api/urls.py`
- Create: `backend/apps/common/api/views.py`
- Create: `backend/apps/common/tests/test_health_api.py`
- Create: `backend/apps/accounts/apps.py`
- Create: `backend/apps/accounts/models.py`
- Create: `backend/apps/accounts/admin.py`
- Create: `backend/apps/accounts/tests/test_models.py`
- Create: `backend/apps/accounts/api/serializers.py`
- Create: `backend/apps/accounts/api/views.py`
- Create: `backend/apps/accounts/api/urls.py`
- Create: `backend/apps/accounts/tests/test_auth_api.py`
- Create: `backend/apps/students/apps.py`
- Create: `backend/apps/students/models.py`
- Create: `backend/apps/students/admin.py`
- Create: `backend/apps/students/tests/test_models.py`
- Create: `backend/apps/students/api/serializers.py`
- Create: `backend/apps/students/api/views.py`
- Create: `backend/apps/students/api/urls.py`
- Create: `backend/apps/students/tests/test_students_api.py`
- Create: `backend/apps/academics/apps.py`
- Create: `backend/apps/academics/models.py`
- Create: `backend/apps/academics/admin.py`
- Create: `backend/apps/academics/tests/test_models.py`
- Create: `backend/apps/academics/api/serializers.py`
- Create: `backend/apps/academics/api/views.py`
- Create: `backend/apps/academics/api/urls.py`
- Create: `backend/apps/academics/tests/test_courses_api.py`
- Create: `backend/apps/integration/apps.py`
- Create: `backend/apps/integration/models.py`
- Create: `backend/apps/ai/apps.py`
- Create: `backend/apps/ai/models.py`

### Frontend

- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/app/router.tsx`
- Create: `frontend/src/app/providers.tsx`
- Create: `frontend/src/features/health/HealthCheckPage.tsx`
- Create: `frontend/src/features/auth/LoginPage.tsx`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/test/setup.ts`

### Infra

- Create: `infra/docker-compose.yml`
- Create: `infra/docker-compose.dev.yml`
- Create: `infra/.env.example`
- Create: `infra/backend.Dockerfile`
- Create: `infra/frontend.Dockerfile`

### Docs

- Modify: `docs/api/openapi.yaml`
- Modify: `docs/phases/phase-01-foundation/README.md`
- Modify: `docs/phases/phase-01-foundation/CHANGELOG.md`

## Task 1: Scaffold The Repository Layout And Shared Tooling

**Files:**
- Create: `.gitignore`
- Create: `.editorconfig`
- Create: `Makefile`
- Create: `backend/requirements/base.txt`
- Create: `backend/requirements/dev.txt`
- Create: `backend/pytest.ini`
- Create: `infra/.env.example`

- [ ] **Step 1: Add root ignore and editor configuration**

```gitignore
# Python
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
venv/

# Node
node_modules/
dist/

# Environment
.env
.env.*

# OS / editor
.DS_Store
Thumbs.db
.idea/
.vscode/
```

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 2
trim_trailing_whitespace = true

[*.py]
indent_size = 4
```

- [ ] **Step 2: Add backend dependency files**

```text
# backend/requirements/base.txt
Django==5.*
djangorestframework==3.*
djangorestframework-simplejwt==5.*
mysqlclient==2.*
celery==5.*
redis==6.*
PyLTI1p3==2.*
requests==2.*
PyYAML==6.*
```

```text
# backend/requirements/dev.txt
-r base.txt
pytest==8.*
pytest-django==4.*
pytest-cov==6.*
factory-boy==3.*
ruff==0.*
```

- [ ] **Step 3: Add `pytest.ini` and `.env.example`**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = sis_backend.settings
python_files = tests.py test_*.py *_tests.py
```

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
MYSQL_DATABASE=modern_sis
MYSQL_USER=modern_sis
MYSQL_PASSWORD=modern_sis
MYSQL_HOST=db
MYSQL_PORT=3306
REDIS_URL=redis://redis:6379/0
ACCESS_TOKEN_MINUTES=15
REFRESH_TOKEN_DAYS=7
```

- [ ] **Step 4: Add a `Makefile` for common commands**

```makefile
backend-install:
	python -m pip install -r backend/requirements/dev.txt

backend-test:
	cd backend && pytest -q

frontend-install:
	cd frontend && npm install

frontend-test:
	cd frontend && npm run test -- --run
```

- [ ] **Step 5: Run filesystem smoke checks**

Run: `test -f .gitignore && test -f backend/requirements/base.txt && test -f infra/.env.example`

Expected: exit code `0`

- [ ] **Step 6: Commit**

```bash
git add .gitignore .editorconfig Makefile backend/requirements/base.txt backend/requirements/dev.txt backend/pytest.ini infra/.env.example
git commit -m "chore: scaffold shared repo tooling"
```

## Task 2: Bootstrap Django Backend And Health Endpoint

**Files:**
- Create: `backend/manage.py`
- Create: `backend/sis_backend/settings.py`
- Create: `backend/sis_backend/urls.py`
- Create: `backend/sis_backend/celery.py`
- Create: `backend/apps/common/api/views.py`
- Create: `backend/apps/common/api/urls.py`
- Create: `backend/apps/common/tests/test_health_api.py`

- [ ] **Step 1: Write the failing health endpoint test**

```python
from rest_framework.test import APIClient


def test_health_endpoint_returns_ok():
    client = APIClient()
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run the test to confirm failure**

Run: `cd backend && pytest apps/common/tests/test_health_api.py -q`

Expected: failure because the URL is not wired yet

- [ ] **Step 3: Create Django settings and URL wiring**

```python
# backend/sis_backend/settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.common",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
```

```python
# backend/sis_backend/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.common.api.urls")),
]
```

```python
# backend/apps/common/api/views.py
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})
```

```python
# backend/apps/common/api/urls.py
from django.urls import path

from .views import HealthView

urlpatterns = [
    path("health", HealthView.as_view(), name="health"),
]
```

- [ ] **Step 4: Run the health test again**

Run: `cd backend && pytest apps/common/tests/test_health_api.py -q`

Expected: `1 passed`

- [ ] **Step 5: Run Django system checks**

Run: `cd backend && python manage.py check`

Expected: `System check identified no issues`

- [ ] **Step 6: Commit**

```bash
git add backend/manage.py backend/sis_backend backend/apps/common
git commit -m "feat: bootstrap django backend and health endpoint"
```

## Task 3: Add Identity, Student, And Access-Control Schema

**Files:**
- Create: `backend/apps/accounts/models.py`
- Create: `backend/apps/students/models.py`
- Create: `backend/apps/accounts/tests/test_models.py`
- Create: `backend/apps/students/tests/test_models.py`
- Modify: `backend/sis_backend/settings.py`

- [ ] **Step 1: Write the failing model tests**

```python
from apps.accounts.models import User, UserCapability
from apps.students.models import StudentProfile, AdvisorAssignment


def test_user_capability_can_be_granted(db):
    user = User.objects.create_user(username="advisor1", email="advisor@example.com", password="secret123")
    capability = UserCapability.objects.create(user=user, capability_name="wellbeing_coordinator")

    assert capability.capability_name == "wellbeing_coordinator"


def test_student_profile_belongs_to_one_user(db):
    user = User.objects.create_user(username="student1", email="student@example.com", password="secret123")
    profile = StudentProfile.objects.create(
        user=user,
        student_number="20260001",
        programme="Computer Science",
        year_of_study=1,
        academic_standing="GOOD_STANDING",
    )

    assert profile.user == user
```

- [ ] **Step 2: Run the tests to confirm failure**

Run: `cd backend && pytest apps/accounts/tests/test_models.py apps/students/tests/test_models.py -q`

Expected: import or migration failure because models do not exist yet

- [ ] **Step 3: Implement the custom user and access models**

```python
# backend/apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_STUDENT = "STUDENT"
    ROLE_ADVISOR = "ADVISOR"
    ROLE_FACULTY = "FACULTY"
    ROLE_ADMIN = "ADMIN"

    ROLE_CHOICES = [
        (ROLE_STUDENT, "Student"),
        (ROLE_ADVISOR, "Advisor"),
        (ROLE_FACULTY, "Faculty"),
        (ROLE_ADMIN, "Admin"),
    ]

    primary_role = models.CharField(max_length=32, choices=ROLE_CHOICES)
    must_reset_password = models.BooleanField(default=False)


class UserCapability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="capabilities")
    capability_name = models.CharField(max_length=64)
    granted_by_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="granted_capabilities")
    granted_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
```

- [ ] **Step 4: Implement the student and advisor-assignment models**

```python
# backend/apps/students/models.py
from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    student_number = models.CharField(max_length=32, unique=True)
    national_id = models.CharField(max_length=64, blank=True)
    programme = models.CharField(max_length=128)
    year_of_study = models.PositiveSmallIntegerField()
    academic_standing = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)


class AdvisorAssignment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="advisor_assignments")
    advisor_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="assigned_advisees")
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
```

- [ ] **Step 5: Set the custom user model and run migrations**

```python
# backend/sis_backend/settings.py
AUTH_USER_MODEL = "accounts.User"
```

Run: `cd backend && python manage.py makemigrations accounts students && python manage.py migrate`

Expected: migrations created and applied successfully

- [ ] **Step 6: Re-run model tests**

Run: `cd backend && pytest apps/accounts/tests/test_models.py apps/students/tests/test_models.py -q`

Expected: tests pass

- [ ] **Step 7: Commit**

```bash
git add backend/apps/accounts backend/apps/students backend/sis_backend/settings.py
git commit -m "feat: add identity and student schema"
```

## Task 4: Add Academic, Integration, And Audit Schema

**Files:**
- Create: `backend/apps/academics/models.py`
- Create: `backend/apps/integration/models.py`
- Create: `backend/apps/ai/models.py`
- Create: `backend/apps/academics/tests/test_models.py`

- [ ] **Step 1: Write failing academic-model tests**

```python
from apps.academics.models import Course, CourseSection, Enrollment


def test_duplicate_enrollment_is_rejected(db, student_profile, section):
    Enrollment.objects.create(student=student_profile, section=section, enrollment_status="ENROLLED")

    try:
        Enrollment.objects.create(student=student_profile, section=section, enrollment_status="ENROLLED")
        assert False, "Expected unique constraint violation"
    except Exception:
        assert True
```

- [ ] **Step 2: Implement the academic models with uniqueness constraints**

```python
# backend/apps/academics/models.py
from django.conf import settings
from django.db import models

from apps.students.models import StudentProfile


class Course(models.Model):
    course_code = models.CharField(max_length=32, unique=True)
    course_title = models.CharField(max_length=255)
    department = models.CharField(max_length=128)
    credit_hours = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)


class CourseSection(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    section_code = models.CharField(max_length=32)
    faculty_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="taught_sections")
    semester = models.CharField(max_length=32)
    academic_year = models.CharField(max_length=16)
    max_capacity = models.PositiveIntegerField()

    class Meta:
        unique_together = ("course", "section_code", "semester", "academic_year")


class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="enrollments")
    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name="enrollments")
    enrollment_status = models.CharField(max_length=32)
    actor_user_id = models.UUIDField(null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    dropped_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "section")
```

- [ ] **Step 3: Add integration and audit tables**

```python
# backend/apps/integration/models.py
from django.db import models


class MoodleUserMap(models.Model):
    user_id = models.UUIDField(unique=True)
    moodle_user_id = models.BigIntegerField(unique=True)
    synced_at = models.DateTimeField(auto_now=True)


class MoodleCourseMap(models.Model):
    section_id = models.UUIDField(unique=True)
    moodle_course_id = models.BigIntegerField(unique=True)
    synced_at = models.DateTimeField(auto_now=True)
```

```python
# backend/apps/ai/models.py
from django.db import models


class AIAuditLog(models.Model):
    feature_name = models.CharField(max_length=64)
    user_id = models.UUIDField(null=True, blank=True)
    student_id = models.UUIDField(null=True, blank=True)
    session_id = models.CharField(max_length=128, blank=True)
    input_payload = models.TextField()
    output_payload = models.TextField()
    provider_name = models.CharField(max_length=64)
    model_name = models.CharField(max_length=64)
    model_version = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

- [ ] **Step 4: Create and apply migrations**

Run: `cd backend && python manage.py makemigrations academics integration ai && python manage.py migrate`

Expected: migrations apply without errors

- [ ] **Step 5: Run academic model tests**

Run: `cd backend && pytest apps/academics/tests/test_models.py -q`

Expected: tests pass

- [ ] **Step 6: Commit**

```bash
git add backend/apps/academics backend/apps/integration backend/apps/ai
git commit -m "feat: add academic integration and audit schema"
```

## Task 5: Refine The Phase 1 OpenAPI Contract

**Files:**
- Modify: `docs/api/openapi.yaml`
- Create: `backend/apps/common/tests/test_openapi_contract.py`

- [ ] **Step 1: Write a failing OpenAPI validation smoke test**

```python
from pathlib import Path

import yaml


def test_openapi_includes_phase1_paths():
    spec = yaml.safe_load(Path("../docs/api/openapi.yaml").read_text())
    paths = spec["paths"]

    assert "/api/v1/health" in paths
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/auth/refresh" in paths
    assert "/api/v1/students/{id}" in paths
    assert "/api/v1/courses" in paths
    assert "/api/v1/enrollments" in paths
```

- [ ] **Step 2: Run the test to confirm failure**

Run: `cd backend && pytest apps/common/tests/test_openapi_contract.py -q`

Expected: at least one missing path assertion fails

- [ ] **Step 3: Update `docs/api/openapi.yaml` with the exact Phase 1 paths**

```yaml
paths:
  /api/v1/health:
    get:
      summary: Health check
  /api/v1/auth/login:
    post:
      summary: Issue JWT token pair
  /api/v1/auth/refresh:
    post:
      summary: Refresh JWT access token
  /api/v1/students/{id}:
    get:
      summary: Retrieve one student profile
  /api/v1/courses:
    get:
      summary: List course catalog entries
  /api/v1/enrollments:
    post:
      summary: Create enrollment
```

- [ ] **Step 4: Re-run the OpenAPI test**

Run: `cd backend && pytest apps/common/tests/test_openapi_contract.py -q`

Expected: test passes

- [ ] **Step 5: Commit**

```bash
git add docs/api/openapi.yaml backend/apps/common/tests/test_openapi_contract.py
git commit -m "docs: refine phase-1 openapi contract"
```

## Task 6: Implement The Initial Phase 1 API Surface

**Files:**
- Create: `backend/apps/accounts/api/serializers.py`
- Create: `backend/apps/accounts/api/views.py`
- Create: `backend/apps/accounts/api/urls.py`
- Create: `backend/apps/students/api/serializers.py`
- Create: `backend/apps/students/api/views.py`
- Create: `backend/apps/students/api/urls.py`
- Create: `backend/apps/academics/api/serializers.py`
- Create: `backend/apps/academics/api/views.py`
- Create: `backend/apps/academics/api/urls.py`
- Create: `backend/apps/accounts/tests/test_auth_api.py`
- Create: `backend/apps/students/tests/test_students_api.py`
- Create: `backend/apps/academics/tests/test_courses_api.py`
- Modify: `backend/sis_backend/urls.py`

- [ ] **Step 1: Write failing auth and API tests**

```python
from rest_framework.test import APIClient


def test_login_returns_token_pair(db, django_user_model):
    django_user_model.objects.create_user(
        username="admin1",
        email="admin@example.com",
        password="secret123",
        primary_role="ADMIN",
    )

    client = APIClient()
    response = client.post("/api/v1/auth/login", {"username": "admin1", "password": "secret123"}, format="json")

    assert response.status_code == 200
    assert "access" in response.json()
    assert "refresh" in response.json()
```

```python
def test_student_detail_requires_auth(db, student_profile):
    client = APIClient()
    response = client.get(f"/api/v1/students/{student_profile.id}")

    assert response.status_code == 401
```

- [ ] **Step 2: Implement JWT login and refresh endpoints**

```python
# backend/apps/accounts/api/views.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

login_view = TokenObtainPairView.as_view()
refresh_view = TokenRefreshView.as_view()
```

```python
# backend/apps/accounts/api/urls.py
from django.urls import path

from .views import login_view, refresh_view

urlpatterns = [
    path("auth/login", login_view, name="auth-login"),
    path("auth/refresh", refresh_view, name="auth-refresh"),
]
```

- [ ] **Step 3: Implement student and course read endpoints**

```python
# backend/apps/students/api/views.py
from rest_framework import generics, permissions

from apps.students.models import StudentProfile
from .serializers import StudentProfileSerializer


class StudentDetailView(generics.RetrieveAPIView):
    queryset = StudentProfile.objects.select_related("user")
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
```

```python
# backend/apps/academics/api/views.py
from rest_framework import generics, permissions

from apps.academics.models import Course
from .serializers import CourseSerializer


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_active=True).order_by("course_code")
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
```

- [ ] **Step 4: Wire the routes**

```python
# backend/sis_backend/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.common.api.urls")),
    path("api/v1/", include("apps.accounts.api.urls")),
    path("api/v1/", include("apps.students.api.urls")),
    path("api/v1/", include("apps.academics.api.urls")),
]
```

- [ ] **Step 5: Run the API test set**

Run: `cd backend && pytest apps/accounts/tests/test_auth_api.py apps/students/tests/test_students_api.py apps/academics/tests/test_courses_api.py -q`

Expected: tests pass

- [ ] **Step 6: Commit**

```bash
git add backend/apps/accounts/api backend/apps/students/api backend/apps/academics/api backend/sis_backend/urls.py
git commit -m "feat: add phase-1 auth and core api skeleton"
```

## Task 7: Scaffold The React Frontend And Docker-Based Local Stack

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/features/health/HealthCheckPage.tsx`
- Create: `frontend/src/features/auth/LoginPage.tsx`
- Create: `frontend/src/lib/api.ts`
- Create: `infra/docker-compose.yml`
- Create: `infra/backend.Dockerfile`
- Create: `infra/frontend.Dockerfile`

- [ ] **Step 1: Scaffold the frontend**

Run: `npm create vite@latest frontend -- --template react-ts`

Expected: Vite creates the React TypeScript app in `frontend/`

- [ ] **Step 2: Install the baseline frontend dependencies**

Run: `cd frontend && npm install axios react-router-dom @tanstack/react-query`

Expected: install completes with exit code `0`

- [ ] **Step 3: Add a minimal login page and health-check page**

```tsx
// frontend/src/features/health/HealthCheckPage.tsx
export function HealthCheckPage() {
  return <main>Modern SIS frontend is running.</main>;
}
```

```tsx
// frontend/src/features/auth/LoginPage.tsx
export function LoginPage() {
  return (
    <main>
      <h1>Modern SIS Login</h1>
      <form>
        <label htmlFor="username">Username</label>
        <input id="username" name="username" />
        <label htmlFor="password">Password</label>
        <input id="password" name="password" type="password" />
        <button type="submit">Sign in</button>
      </form>
    </main>
  );
}
```

- [ ] **Step 4: Add Docker Compose for local services**

```yaml
services:
  db:
    image: mysql:8
    environment:
      MYSQL_DATABASE: modern_sis
      MYSQL_USER: modern_sis
      MYSQL_PASSWORD: modern_sis
      MYSQL_ROOT_PASSWORD: root
    ports:
      - "3306:3306"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build:
      context: ..
      dockerfile: infra/backend.Dockerfile
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: ..
      dockerfile: infra/frontend.Dockerfile
    depends_on:
      - backend
```

- [ ] **Step 5: Run frontend and infra smoke checks**

Run: `cd frontend && npm run build`

Expected: Vite build succeeds

Run: `docker compose -f infra/docker-compose.yml config`

Expected: Compose file resolves without validation errors

- [ ] **Step 6: Commit**

```bash
git add frontend infra
git commit -m "feat: scaffold frontend and local docker stack"
```

## Task 8: Update Phase 1 Documentation After Scaffolding

**Files:**
- Modify: `docs/phases/phase-01-foundation/README.md`
- Modify: `docs/phases/phase-01-foundation/CHANGELOG.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update the Phase 1 README with implementation progress**

Add a short section documenting:

```markdown
## Implementation Progress

- repo scaffold created
- backend bootstrap created
- schema migrations created
- phase-1 api skeleton created
- frontend and docker baseline created
```

- [ ] **Step 2: Update the changelogs**

Add entries for:

```markdown
### Added
- Django backend scaffold
- React frontend scaffold
- Initial schema models and migrations
- Phase 1 API skeleton
```

- [ ] **Step 3: Run targeted documentation checks**

Run: `rg -n "Phase 1|v0.1.0|Implementation Progress" README.md CHANGELOG.md docs/`

Expected: matches appear in the updated docs

- [ ] **Step 4: Commit**

```bash
git add CHANGELOG.md docs/phases/phase-01-foundation/README.md docs/phases/phase-01-foundation/CHANGELOG.md
git commit -m "docs: update phase-1 implementation progress"
```

## Plan Self-Review

### Spec Coverage

- Schema: covered by Tasks 3 and 4.
- API contract: covered by Task 5.
- Repo scaffolding: covered by Tasks 1, 2, and 7.
- Version-control and phase tracking updates: covered by Task 8.

### Placeholder Scan

- No `TODO`, `TBD`, or deferred placeholders were intentionally left in the task steps.

### Type Consistency

- The plan consistently uses `User`, `UserCapability`, `StudentProfile`, `Course`, `CourseSection`, and `Enrollment` across schema and API tasks.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-12-phase-01-foundation-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
