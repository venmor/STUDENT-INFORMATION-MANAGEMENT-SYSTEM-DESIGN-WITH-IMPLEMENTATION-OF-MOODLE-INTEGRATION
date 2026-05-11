# Phase 6 - Opt-In Wellbeing Support

## Overview

Phase 6 introduces the Opt-In Wellbeing Support module, providing students with a private, consent-driven pathway to signal emotional or personal difficulty, and routing appropriate resources or staff escalation.

## Step 6.1 - Wellbeing Foundation and Check-in

### Features

- **Wellbeing Consent:** explicit opt-in/opt-out flow for students (AI-WBE-001)
- **Wellbeing Check-in:** mood rating (1-5) and optional free-text (AI-WBE-002)
- **Triage Engine:** deterministic rules for resource routing or staff escalation (AI-WBE-003)
- **Escalation Notifications:** real-time alerts for wellbeing coordinators (AI-WBE-004)
- **Restricted Storage:** wellbeing records isolated from general admin views (AI-WBE-006)
- **Data Deletion:** students can delete their history at any time (AI-WBE-009)

### Planned Architecture

```
apps.wellbeing/
  models.py          - WellbeingConsent, WellbeingCheckIn
  services.py        - Triage and escalation logic
  views.py           - Student check-in and coordinator dashboard
  urls.py            - Route definitions
  serializers.py     - Check-in and triage serializers
```

### Governance

- Wellbeing data is excluded from general AI audit logs.
- Restricted audit logging for safeguarding metadata only.
- Strict primary role + `wellbeing_coordinator` capability check for staff access.
