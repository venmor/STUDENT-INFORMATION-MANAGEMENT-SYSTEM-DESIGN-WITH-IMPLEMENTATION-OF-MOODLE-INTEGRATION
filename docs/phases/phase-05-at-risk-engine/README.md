# Phase 5 - At-Risk Student Insight Engine

## Overview

Phase 5 introduces the At-Risk Student Insight Engine, a nightly processing system that evaluates 9 distinct risk signals per active student, classifies severity using weighted rules, generates deterministic explanations for Medium/High alerts, and surfaces actionable alerts in the advisor dashboard with an acknowledge/history workflow.

## Step 5.1 - At-Risk Engine Foundation

**Status:** Complete

### Features

- **9 Signal Evaluators:** attendance_flag, academic_probation, financial_hold, grade_decline, incomplete_grade, moodle_inactivity, assignment_miss_rate, quiz_failure_pattern, forum_disengagement
- **Severity Classifier:** HIGH (any 1 high-weight signal or 3+ total), MEDIUM (2 medium or 1 medium + 2 low), LOW (1 isolated signal)
- **Deterministic Explanation Provider:** Builds readable alert text without AI API calls
- **Advisor Dashboard API:** GET open alerts, GET history, POST acknowledge
- **Management Commands:** `run_at_risk_engine` for manual/scheduled execution, `seed_at_risk_demo` for demo data
- **Access Control:** Advisor and Admin roles only

### Architecture

```
apps.atrisk/
  config.py          - Signal thresholds and display names
  signals.py         - 9 evaluator functions (evaluate_all_signals)
  services.py        - Orchestration: evaluate -> classify -> explain -> store
  models.py          - AtRiskAlert with severity, signals, explanation
  views.py           - DRF APIViews for alerts list, history, acknowledge
  urls.py            - Route definitions
  serializers.py     - AtRiskAlertSerializer with student context
  admin.py           - Django admin registration
  management/commands/
    run_at_risk_engine.py
    seed_at_risk_demo.py
  tests/
    test_signals.py
    test_classifier.py
    test_services.py
    test_api.py
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/advisor/at-risk/alerts` | Open alerts sorted by severity desc, date desc |
| GET | `/api/v1/advisor/at-risk/history` | Acknowledged alerts |
| POST | `/api/v1/advisor/at-risk/alerts/{id}/acknowledge` | Acknowledge an alert |

### Configuration (AI-RSK-008)

Signal thresholds are defined in `apps/atrisk/config.py` and can be adjusted without code changes to the evaluators.

### Audit Integration (AI-RSK-009)

- New alerts are logged to `AIAuditLog` with action `AT_RISK_EVALUATION`
- Engine runs are logged to `AuditEvent` with action `AT_RISK_ENGINE_RUN`
- Acknowledgements are logged to `AuditEvent` with action `AT_RISK_ALERT_ACKNOWLEDGED`

### Notes

- Uses deterministic provider only (no OpenAI API calls)
- Designed for nightly Celery task execution (management command provides same logic)
- Auto-close logic resolves alerts when student signals clear
