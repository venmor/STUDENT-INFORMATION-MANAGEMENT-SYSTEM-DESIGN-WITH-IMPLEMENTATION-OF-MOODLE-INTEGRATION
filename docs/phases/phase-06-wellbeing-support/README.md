# Phase 6 - Opt-In Wellbeing Support

## Overview

Phase 6 introduces the Opt-In Wellbeing Support module, providing students with a private, consent-driven pathway to signal emotional or personal difficulty, and routing appropriate resources or staff escalation.

## Step 6.1 - Policy and Staffing Gate

**Status:** Confirmed

### Policy Approvals
The following institutional policies have been reviewed and approved for Wave 6 rollout:
- **Consent Language:** Plain-language statement explaining data collection, access, and deletion rights.
- **Retention Schedule:** Wellbeing check-ins are retained for the duration of the student's enrollment unless deleted by the student.
- **Deletion Policy:** Students can irreversibly delete their history at any time; free-text is removed within 24 hours.
- **Escalation Process:** High-risk (Escalate) check-ins trigger immediate notification to the Wellbeing Coordinator and display local crisis contacts to the student.

### Staffing Readiness
- **Wellbeing Coordinators:** At least one staff member (e.g., `advisor.demo` in dev) is assigned the `wellbeing_coordinator` capability.
- **Response Protocol:** Coordinators are trained to respond to `Escalate` notifications within 4 business hours.

### Technical Design Review
- **Restricted Schema:** Wellbeing records are isolated from general SIS and AI audit logs.
- **Safeguarding Audit:** `wellbeing_audit_log` stores only minimal metadata (event ID, triage class, notification status).

## Step 6.2 - Wellbeing Foundation and Check-in

### Features

- **Wellbeing Consent (AI-WBE-001):** explicit opt-in/opt-out flow for students.
- **Wellbeing Check-in (AI-WBE-002):** mood rating (1-5) and optional free-text.
- **Triage Engine (AI-WBE-003):** deterministic rules for resource routing or staff escalation.
  - `Normal`: Mood >= 3, no distress keywords.
  - `Concerning`: Mood = 2, or moderate distress keywords.
  - `Escalate`: Mood = 1, or immediate risk keywords.
- **Escalation Notifications (AI-WBE-004):** real-time alerts for wellbeing coordinators.
- **Restricted Storage (AI-WBE-006):** wellbeing records isolated from general admin/advisor views.
- **Data Deletion (AI-WBE-009):** students can delete their history at any time.
- **Mood Reporting (AI-WBE-007):** Anonymized weekly trends for institutional planning.

### Architecture

```
apps.wellbeing/
  models.py          - WellbeingConsent, WellbeingCheckIn, WellbeingAuditLog
  services.py        - Triage engine, notification hooks, history management
  views.py           - Student and Coordinator endpoints
  urls.py            - Route definitions
  serializers.py     - Check-in and reporting serializers
  permissions.py     - Strict capability-based access
```

### API Endpoints

| Method | Path | Description | Role |
|--------|------|-------------|------|
| GET | `/api/v1/wellbeing/consent` | Check current consent status | Student |
| POST | `/api/v1/wellbeing/consent` | Update consent (opt-in/out) | Student |
| POST | `/api/v1/wellbeing/triage` | Submit a new check-in | Student |
| GET | `/api/v1/wellbeing/history` | View own check-in history | Student |
| DELETE | `/api/v1/wellbeing/history/{id}` | Delete a specific check-in | Student |
| DELETE | `/api/v1/wellbeing/history/purge` | Delete entire history | Student |
| GET | `/api/v1/wellbeing/coordinator/alerts` | Active escalation list | Coordinator |
| GET | `/api/v1/wellbeing/reporting/trends` | Anonymized aggregates | Admin |

### Governance

- Wellbeing data is excluded from general AI audit logs.
- Restricted audit logging for safeguarding metadata only.
- Strict primary role + `wellbeing_coordinator` capability check for staff access.

## Verification Commands

### Backend Tests
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
cd backend
pytest apps/wellbeing/tests/ --ds=sis_backend.test_settings
```

### Frontend Unit Tests
```bash
cd frontend
npm test tests/unit/wellbeing-page.test.tsx
```

### Manual Verification
1. Log in as a student (e.g., `student.demo1`).
2. Navigate to `/student/wellbeing`.
3. Click "Enable Wellbeing Check-In".
4. Submit a mood rating (e.g., 4).
5. Verify "Thank you" message and entry in "Recent History".
6. Submit an `Escalate` rating (1) or a comment with "harm".
7. Verify "We're here to help" escalation screen and resource display.
