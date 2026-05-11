# Phase 2 Step 2.3 Close-Out Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the remaining backend and documentation gaps so Phase 2 Step 2.3 satisfies the setup guide and current SRS-backed backend contract, and leaves the project ready for Step 2.4 frontend work.

**Architecture:** Extend the existing Django apps rather than introducing new layers. Keep the close-out focused on missing Step 2.3 backend contract surface: stricter grade validation, read endpoints for frontend consumption, completion of student-record workflows, and documentation alignment. Preserve the route-policy RBAC model and add only the minimum models and endpoints needed for Step 2.4 readiness.

**Tech Stack:** Django 5, Django REST Framework, MySQL 8, pytest, pytest-django, ruff, OpenAPI YAML

---

## File Structure Map

- Modify: `backend/apps/academics/api/serializers.py`
- Modify: `backend/apps/academics/api/urls.py`
- Modify: `backend/apps/academics/api/views.py`
- Modify: `backend/apps/academics/models.py`
- Modify: `backend/apps/academics/services.py`
- Modify: `backend/apps/academics/tests/test_courses_api.py`
- Modify: `backend/apps/academics/tests/test_grades_api.py`
- Modify: `backend/apps/accounts/access.py`
- Modify: `backend/apps/students/api/serializers.py`
- Modify: `backend/apps/students/api/urls.py`
- Modify: `backend/apps/students/api/views.py`
- Modify: `backend/apps/students/models.py`
- Modify: `backend/apps/students/tests/test_students_api.py`
- Create: `backend/apps/students/migrations/0002_studentcorrectionrequest.py`
- Modify: `docs/api/openapi.yaml`
- Modify: `docs/phases/phase-02-core-build/README.md`
- Modify: `docs/phases/phase-02-core-build/CHANGELOG.md`
- Modify: `backend/README.md`

## Task 1: Add Failing Tests For The Remaining Step 2.3 Contract

**Files:**
- Modify: `backend/apps/academics/tests/test_courses_api.py`
- Modify: `backend/apps/academics/tests/test_grades_api.py`
- Modify: `backend/apps/students/tests/test_students_api.py`

- [x] Add failing tests for:
  - grade creation rejecting non-enrolled students
  - student-facing/advisor-facing/admin-facing grade history reads
  - section listing and section roster reads for assigned faculty/admin
  - financial flag update and clear flows
  - advising note update flow with audit visibility preserved
  - attendance percentage exposure on student detail
  - academic standing override requiring a reason
  - student correction request submission and admin review flow
  - student course-detail restriction to programme-relevant courses

- [x] Run targeted red-phase commands and confirm the new tests fail for the intended reasons:
  - `MYSQL_HOST=127.0.0.1 MYSQL_PORT=3313 MYSQL_DATABASE=modern_sis MYSQL_USER=root MYSQL_PASSWORD=root DJANGO_SECRET_KEY=dev-secret /tmp/modern-sis-audit-venv/bin/pytest -q apps/academics/tests/test_grades_api.py -k "non_enrolled or history"`
  - `MYSQL_HOST=127.0.0.1 MYSQL_PORT=3313 MYSQL_DATABASE=modern_sis MYSQL_USER=root MYSQL_PASSWORD=root DJANGO_SECRET_KEY=dev-secret /tmp/modern-sis-audit-venv/bin/pytest -q apps/academics/tests/test_courses_api.py -k "roster or section_list or course_detail"`
  - `MYSQL_HOST=127.0.0.1 MYSQL_PORT=3313 MYSQL_DATABASE=modern_sis MYSQL_USER=root MYSQL_PASSWORD=root DJANGO_SECRET_KEY=dev-secret /tmp/modern-sis-audit-venv/bin/pytest -q apps/students/tests/test_students_api.py -k "financial or advising or correction or attendance or override"`

### Implemented

- Added regression coverage in `backend/apps/academics/tests/test_courses_api.py` for section reads, roster reads, and programme-filtered course/section detail access.
- Added regression coverage in `backend/apps/academics/tests/test_grades_api.py` for enrollment-aware grade writes and role-scoped grade list reads.
- Added regression coverage in `backend/apps/students/tests/test_students_api.py` for financial-flag updates, advising-note updates with audit logging, attendance percentages, standing override validation, and correction-request review flow.
- Confirmed the new tests failed against the pre-close-out backend surface before implementation.

## Task 2: Complete The Academics Read Surface And Grade Validation

**Files:**
- Modify: `backend/apps/academics/api/serializers.py`
- Modify: `backend/apps/academics/api/urls.py`
- Modify: `backend/apps/academics/api/views.py`
- Modify: `backend/apps/academics/models.py`
- Modify: `backend/apps/academics/services.py`
- Modify: `backend/apps/accounts/access.py`

- [x] Implement enrollment validation in grade creation/update paths so grades can only exist for active enrolled students in the target section.
- [x] Add section list and roster endpoints with role-aware access for admin and assigned faculty, and programme-filtered reads for students where applicable.
- [x] Add grade list/history endpoints that expose:
  - students: own official grades only
  - advisors: official grades for assigned advisees
  - faculty: grades for their own sections
  - admins: full visibility
- [x] Restrict course detail and section detail reads so students cannot bypass programme filtering by direct object lookup.
- [x] Re-run the targeted academics tests until green.

### Implemented

- Added active-enrollment validation in `backend/apps/academics/services.py` and applied it to grade create, update, and officialise paths.
- Extended `backend/apps/academics/api/views.py` so `/api/v1/sections` supports list reads, `/api/v1/sections/<section_id>/roster` returns enrolled roster data, and `/api/v1/grades` supports role-scoped list reads.
- Extended serializers in `backend/apps/academics/api/serializers.py` with roster payloads, richer section metadata, and grade history fields needed by Step 2.4 dashboards.
- Updated `backend/apps/accounts/access.py` so the new academics routes are covered by route-policy RBAC.

## Task 3: Complete Student Record Workflows

**Files:**
- Modify: `backend/apps/students/models.py`
- Create: `backend/apps/students/migrations/0002_step23_closeout.py`
- Modify: `backend/apps/students/api/serializers.py`
- Modify: `backend/apps/students/api/urls.py`
- Modify: `backend/apps/students/api/views.py`
- Modify: `backend/apps/accounts/access.py`

- [x] Add the minimal student-correction-request model and API workflow needed for `FR-STU-005`.
- [x] Add update/clear endpoints for financial flags.
- [x] Add update support for advising notes while keeping approval behavior explicit and audited.
- [x] Expose attendance percentages alongside attendance flags on student detail responses.
- [x] Add an explicit academic-standing override workflow that requires a reason and records the change set in audit metadata.
- [x] Re-run the targeted students tests until green.

### Implemented

- Added `StudentCorrectionRequest` in `backend/apps/students/models.py` plus migration `backend/apps/students/migrations/0002_studentcorrectionrequest.py`.
- Added serializers and views for correction-request submission and admin review, financial-flag update/clear, and advising-note draft updates in `backend/apps/students/api/serializers.py` and `backend/apps/students/api/views.py`.
- Added attendance percentages and standing-override validation to the student detail/update contract.
- Added route-policy coverage for the new students endpoints in `backend/apps/accounts/access.py`.

## Task 4: Refresh Documentation And Contract Artifacts

**Files:**
- Modify: `docs/api/openapi.yaml`
- Modify: `docs/phases/phase-02-core-build/README.md`
- Modify: `docs/phases/phase-02-core-build/CHANGELOG.md`
- Modify: `backend/README.md`

- [x] Update the OpenAPI document to match the final Step 2.3 route surface.
- [x] Update the phase README and changelog to document the Step 2.3 close-out deliverables and verification commands.
- [x] Update backend docs so local verification notes reflect the DB privilege nuance for pytest and the final Step 2.3 capabilities.

### Implemented

- Updated `docs/api/openapi.yaml` for section list and roster reads, grade list reads, financial-flag updates, advising-note updates, correction requests, richer section payloads, richer grade payloads, and attendance percentages on student detail.
- Updated `docs/phases/phase-02-core-build/README.md`, `docs/phases/phase-02-core-build/CHANGELOG.md`, and `backend/README.md` so the written Step 2.3 status matches the verified backend surface.
- Updated `docs/diagrams/modern-sis-erd.md` to include `STUDENT_CORRECTION_REQUESTS`.

## Task 5: Full Verification And Integration

**Files:**
- Verify only

- [x] Remove transient test artifacts from the worktree before final verification.
- [x] Run:
  - `MYSQL_HOST=127.0.0.1 MYSQL_PORT=3313 MYSQL_DATABASE=modern_sis MYSQL_USER=modern_sis MYSQL_PASSWORD=modern_sis DJANGO_SECRET_KEY=dev-secret /tmp/modern-sis-audit-venv/bin/python -m compileall apps sis_backend`
  - `MYSQL_HOST=127.0.0.1 MYSQL_PORT=3313 MYSQL_DATABASE=modern_sis MYSQL_USER=modern_sis MYSQL_PASSWORD=modern_sis DJANGO_SECRET_KEY=dev-secret /tmp/modern-sis-audit-venv/bin/python manage.py check`
  - `MYSQL_HOST=127.0.0.1 MYSQL_PORT=3313 MYSQL_DATABASE=modern_sis MYSQL_USER=modern_sis MYSQL_PASSWORD=modern_sis DJANGO_SECRET_KEY=dev-secret /tmp/modern-sis-audit-venv/bin/python manage.py makemigrations --check --dry-run`
  - `MYSQL_HOST=127.0.0.1 MYSQL_PORT=3313 MYSQL_DATABASE=modern_sis MYSQL_USER=modern_sis MYSQL_PASSWORD=modern_sis DJANGO_SECRET_KEY=dev-secret /tmp/modern-sis-audit-venv/bin/python manage.py migrate --noinput`
  - `MYSQL_HOST=127.0.0.1 MYSQL_PORT=3313 MYSQL_DATABASE=modern_sis MYSQL_USER=root MYSQL_PASSWORD=root DJANGO_SECRET_KEY=dev-secret /tmp/modern-sis-audit-venv/bin/pytest -q --cov=apps --cov-report=term-missing`
  - `python -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('docs/api/openapi.yaml').read_text()); print('openapi yaml ok')"`
- [ ] Commit the Step 2.3 close-out work on a dedicated branch once the remaining unrelated local edit in `docs/project/modern-sis-setup-guide.md` is either committed separately or intentionally left out of the Step 2.3 commit.
- [ ] Push the verified Step 2.3 branch to `origin`.
- [x] Report whether Step 2.3 is now complete and whether the backend contract is ready for Step 2.4.

### Verification Evidence

- Targeted close-out tests passed: `8 passed`
- Full backend verification passed: `43 passed` and `93%` total coverage
- `manage.py check` passed
- `manage.py makemigrations --check --dry-run` reported `No changes detected`
- `manage.py migrate --noinput` applied `students.0002_studentcorrectionrequest`
- OpenAPI YAML parsed successfully

## Outcome

- Step 2.3 is complete from the backend perspective and is ready for Step 2.4 in `docs/project/modern-sis-setup-guide.md`.
- The only clearly unrelated local change still outside the Step 2.3 close-out is the modified `docs/project/modern-sis-setup-guide.md`. It was left untouched to avoid overwriting user work.
