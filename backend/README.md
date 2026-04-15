# Backend

This directory contains the Django backend for Modern SIS.

## Phase 2 Status

Step 2.1 establishes the project baseline:

- Django project scaffold
- environment-driven settings
- MySQL-backed initial migrations
- dependency management under `requirements/`

Step 2.2 adds the authentication and RBAC baseline:

- custom Django user model with primary-role enforcement
- seeded role catalog for `STUDENT`, `ADVISOR`, `FACULTY`, and `ADMIN`
- `wellbeing_coordinator` capability flags
- JWT login and refresh endpoints under `/api/v1/auth/`
- bcrypt-backed password storage via Django's built-in `BCryptSHA256PasswordHasher`
- central API access-control middleware with named route policies instead of view-level role decorators
- advisor/admin and capability-gated probe endpoints for access-control verification

## Local Verification Notes

- Use the application database user for `manage.py check` and `manage.py migrate`.
- Use a MySQL account that can create temporary databases when running `pytest`, because Django creates a separate test schema by default.
