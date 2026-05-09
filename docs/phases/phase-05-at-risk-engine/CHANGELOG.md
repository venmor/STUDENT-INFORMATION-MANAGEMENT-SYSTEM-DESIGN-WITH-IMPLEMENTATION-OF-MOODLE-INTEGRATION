# Phase 5 Changelog

## Step 5.1 - At-Risk Student Insight Engine (2026-05-09)

### Added
- `apps.atrisk` Django app with AtRiskAlert model, severity classification, and 9 signal evaluators
- Deterministic explanation provider for MEDIUM/HIGH severity alerts
- Advisor API endpoints: GET alerts, GET history, POST acknowledge
- Access policies restricting at-risk endpoints to ADVISOR and ADMIN roles
- Management commands: `run_at_risk_engine` and `seed_at_risk_demo`
- Auto-close logic for resolved alerts
- AI audit logging for new alerts (`AT_RISK_EVALUATION` action)
- General audit logging for engine runs and acknowledgements
- Frontend `useAtRiskAlerts` hook with TanStack Query integration
- Live `AtRiskAlertQueue` component replacing placeholder
- Live `AdvisorAlertHistoryPage` with acknowledged alert display
- Backend test coverage: signal evaluators, classifier, services, API permissions
- Configurable signal thresholds in `config.py` (AI-RSK-008)
