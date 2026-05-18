# Supervisor Submission Readme

## Repository Branch

Branch: `supervisor/objective-1-submission`  
Tag: `objective-1-supervisor-submission-v1`

GitHub branch link:

```text
https://github.com/venmor/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/tree/supervisor/objective-1-submission
```

GitHub tag link:

```text
https://github.com/venmor/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION/tree/objective-1-supervisor-submission-v1
```

## Files for Report Submission

- `submission/OBJECTIVE_1_IMPLEMENTATION_REPORT.md`
- `submission/OBJECTIVE_1_IMPLEMENTATION_REPORT.docx`
- `submission/SUBMISSION_README.md`
- `docs/objective-1/SOURCE_MAP.md`

## Source Archive

The source archive is generated from the committed branch with:

```bash
git archive --format=tar.gz --output=objective-1-supervisor-submission-branch.tar.gz supervisor/objective-1-submission
sha256sum objective-1-supervisor-submission-branch.tar.gz > objective-1-supervisor-submission-branch.tar.gz.sha256
```

## How to Run the Submitted System

```bash
git clone git@github.com:venmor/STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION.git
cd STUDENT-INFORMATION-MANAGEMENT-SYSTEM-DESIGN-WITH-IMPLEMENTATION-OF-MOODLE-INTEGRATION
git checkout supervisor/objective-1-submission
cp infra/.env.example infra/.env
cp infra/moodle.env.example infra/moodle.env
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml up --build
```

In a second terminal:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml exec backend python manage.py migrate
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml exec backend python manage.py seed_demo_sis
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml exec backend python manage.py seed_moodle_demo
```

Open:

```text
http://127.0.0.1:8080
```

## How to Test the Submitted System

Backend:

```bash
cd backend
DJANGO_SECRET_KEY=test-secret DJANGO_SETTINGS_MODULE=sis_backend.test_settings MYSQL_DATABASE=test MYSQL_USER=test MYSQL_PASSWORD=test MYSQL_HOST=localhost MYSQL_PORT=3306 pytest apps/accounts apps/students apps/structure apps/academics apps/integration apps/notifications apps/audit apps/calendar apps/reporting apps/documents
```

Frontend:

```bash
cd frontend
npm ci
npm run typecheck
npm run lint
npm test -- --reporter=dot
npm run build
```

Docker configuration:

```bash
docker compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml config
docker compose -f infra/docker-compose.yml -f infra/docker-compose.moodle.yml config
```
