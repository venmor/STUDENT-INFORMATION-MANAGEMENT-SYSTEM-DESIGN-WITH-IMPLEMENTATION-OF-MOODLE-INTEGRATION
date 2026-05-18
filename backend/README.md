# Backend Source for Objective 1

The backend implements the Objective 1 Student Information System API using Django and Django REST Framework.

## Implemented Areas

- Authentication and role-based access for administrator, advisor, faculty, and student users.
- Student profile and academic-record management.
- Academic structure, departments, programmes, courses, terms, and course sections.
- Enrollment, drop, transfer, waitlist, approval, and enrollment-event tracking.
- Grade entry, officialisation, correction requests, release visibility, and audit support.
- Moodle web service provisioning through integration outbox events.
- LTI v1.3 tool-provider launch handling, JWKS publication, launch session storage, and context mapping.
- Notifications, audit activity, academic calendar, reporting, and student document support used by the SIS workflows.

## Main Commands

```bash
python manage.py migrate
python manage.py seed_demo_sis
python manage.py seed_moodle_demo
python manage.py process_moodle_sync --limit 20
python manage.py verify_phase_3_integrations
```

## Focused Test Command

```bash
DJANGO_SECRET_KEY=test-secret DJANGO_SETTINGS_MODULE=sis_backend.test_settings MYSQL_DATABASE=test MYSQL_USER=test MYSQL_PASSWORD=test MYSQL_HOST=localhost MYSQL_PORT=3306 pytest apps/accounts apps/students apps/structure apps/academics apps/integration apps/notifications apps/audit apps/calendar apps/reporting apps/documents
```
