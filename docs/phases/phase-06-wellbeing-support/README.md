# Phase 6 - Opt-In Wellbeing Support

## Overview

Phase 6 introduces the Opt-In Wellbeing Support module, providing students with a private, consent-driven pathway to signal emotional or personal difficulty. The system routes appropriate resources or triggers staff escalation based on a deterministic rules engine.

## Step 6.1 - Policy and Staffing Gate

**Status:** Confirmed & Approved

### Policy Approvals
The following institutional policies have been reviewed and approved for Wave 6 rollout:
- **Consent Language:** A clear, plain-language statement explaining that wellbeing data is restricted to authorized staff and used only for support triage.
- **Retention Schedule:** Records are kept during active enrollment.
- **Deletion Policy:** Students have the "Right to be Forgotten" within this module. Deleting a check-in wipes the mood rating and comment irreversibly from the primary store.
- **Escalation Process:** Triage results marked as `ESCALATE` trigger immediate in-app notifications to Wellbeing Coordinators.

### Staffing Readiness
- **Wellbeing Coordinators:** Staff members assigned the `wellbeing_coordinator` capability are responsible for monitoring and responding to escalations.
- **Runbook:** Coordinators follow the "Wellbeing Response Protocol" for outreaching to students in distress.

## Step 6.2 - Build the opt-in wellbeing support feature

### Features

- **Wellbeing Consent (AI-WBE-001):** Students must explicitly opt-in before any check-in data is collected.
- **Wellbeing Check-in (AI-WBE-002):** A simple 1-5 mood scale ("How are you feeling today?") plus an optional 500-character comment.
- **Triage Engine (AI-WBE-003):**
  - Uses deterministic rules based on mood rating and institution-approved keywords (e.g., 'harm', 'suicide', 'struggling').
  - Classifies into `Normal`, `Concerning`, or `Escalate`.
  - Uses LLM (deterministic provider in dev/test) to generate a supportive empathy message for non-escalation cases.
- **Escalation Notifications (AI-WBE-004):** Real-time alerts for staff with the `wellbeing_coordinator` capability.
- **Restricted Storage (AI-WBE-006):** Data is isolated in `apps.wellbeing`. Comments are excluded from general history views and only accessible to coordinators.
- **Data Deletion (AI-WBE-009):** Students can delete individual entries or purge their entire history. Deletion wipes sensitive fields (`comment`, `mood_rating`) immediately.
- **Mood Reporting (AI-WBE-007):** Anonymized weekly trends (average mood and volume) for institutional administrators.

### Architecture

#### Backend (`apps.wellbeing`)
- **Models:**
  - `WellbeingConsent`: Tracks student opt-in/opt-out state.
  - `WellbeingCheckIn`: Stores mood, comment, and triage result.
  - `WellbeingAuditLog`: Stores minimal metadata for safeguarding compliance.
- **Services:**
  - `process_wellbeing_checkin`: Orchestrates triage, storage, audit, and notifications.
  - `evaluate_triage`: Pure function for deterministic rule matching.
  - `generate_supportive_text`: Integration with AI provider for empathetic feedback.
- **Permissions:**
  - `IsStudent`: Restricts history and check-in to the owner.
  - `IsWellbeingCoordinator`: Grants access to escalation alerts based on capability.

#### Frontend
- **Hooks:** `useWellbeingConsent`, `useWellbeingTriage`, `useWellbeingHistory`.
- **Components:**
  - `MoodSelector`: Visual selection of 1-5 mood scale with descriptive labels.
  - `WellbeingConsentPage`: The initial gate for the feature.
  - `WellbeingCheckInForm`: The main submission interface.
  - `WellbeingEscalationScreen`: Displayed when urgent support is needed.

### API Endpoints

| Method | Path | Description | Role |
|--------|------|-------------|------|
| GET | `/api/v1/wellbeing/consent` | Current opt-in status | Student |
| POST | `/api/v1/wellbeing/consent` | Update opt-in (is_enabled: bool) | Student |
| POST | `/api/v1/ai/wellbeing/triage` | Submit check-in and get triage | Student |
| GET | `/api/v1/wellbeing/history` | List own check-ins (summary only) | Student |
| DELETE | `/api/v1/wellbeing/history/{id}` | Delete/Wipe a check-in | Student |
| GET | `/api/v1/wellbeing/coordinator/alerts` | View active escalations | Coordinator |
| GET | `/api/v1/wellbeing/reporting/trends` | View anonymized mood trends | Admin |

## Verification Commands

### 1. Automated Backend Tests
Ensure the environment is set up, then run:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
cd backend
export DJANGO_SECRET_KEY='test-secret-key-12345'
pytest apps/wellbeing/tests/ --ds=sis_backend.test_settings
```

### 2. Automated Frontend Unit Tests
```bash
cd frontend
npm test tests/unit/wellbeing-page.test.tsx
npm test tests/unit/wellbeing-checkin-form.test.tsx
```

### 3. Manual UI Verification
1. **Login:** As `student.demo1`.
2. **Consent:** Navigate to `Wellbeing` in sidebar. Click "Enable Wellbeing Check-In".
3. **Normal Check-in:** Select "Good" (4), add a comment "Feeling great". Submit. Verify success message and history update.
4. **Escalation Check-in:** Select "Very difficult" (1). Submit. Verify transition to "We're here to help" screen with crisis contacts.
5. **Deletion:** In history, verify you can delete a record.
6. **Coordinator View:** Log in as `advisor.demo` (ensure `wellbeing_coordinator` capability is assigned). Verify the escalation alert is visible in the notification bell or coordinator dashboard.
