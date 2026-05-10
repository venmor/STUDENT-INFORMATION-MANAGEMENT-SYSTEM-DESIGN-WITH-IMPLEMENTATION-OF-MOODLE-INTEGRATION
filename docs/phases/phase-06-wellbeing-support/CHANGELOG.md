# Phase 6 Changelog

## Step 6.1 & 6.2 - Wellbeing Support Foundation (2026-05-10)

### Added
- `apps.wellbeing` Django app for private, consent-driven student support.
- `WellbeingConsent`, `WellbeingCheckIn`, and `WellbeingAuditLog` models.
- Deterministic triage engine with keyword detection (AI-WBE-003).
- Escalation notification system for staff with `wellbeing_coordinator` capability.
- REST API for student consent, triage submission, and history management.
- Coordinator API for viewing active escalations.
- Anonymized mood trend reporting API for administrators.
- Frontend `useWellbeing` hooks and API wiring.
- Live `StudentWellbeingPage` with consent, mood selection, and escalation screens.
- Strict RBAC and capability-based access policies for wellbeing data.
