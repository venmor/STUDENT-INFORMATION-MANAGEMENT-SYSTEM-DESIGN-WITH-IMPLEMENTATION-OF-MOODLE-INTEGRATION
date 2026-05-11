# Phase 3 Step 3.4 Test Matrix

Step 3.4 is the integration-verification and Moodle engagement analytics-ingestion gate. It proves that Step 3.2 SIS-to-Moodle provisioning and Step 3.3 Moodle-to-SIS LTI launches can be verified together, then adds the first Moodle engagement snapshot foundation for later analytics work.

This step does not implement at-risk scoring, AI co-pilot features, wellbeing workflows, Phase 3.5 dashboards, or a BI/reporting system. Live Moodle is optional for normal automated tests; mocked tests remain the default regression path.

## Automated Command Set

Run from `backend/` with the local environment exported:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -q apps/integration/tests/test_verify_moodle_rest_command.py
pytest -q apps/integration/tests/test_moodle_sync_service.py
pytest -q apps/integration/tests/test_process_moodle_sync_command.py
pytest -q apps/integration/tests/test_lti_tool_provider.py
pytest -q apps/integration/tests/
ruff check .
```

Run from `frontend/` when LTI pages change:

```bash
npm run typecheck
npm run lint
npm test
npm run build
```

## Matrix

| Test ID | Purpose | Preconditions | Data Setup | Steps | Expected Result | Status | Requirement | Notes / Troubleshooting |
|---|---|---|---|---|---|---|---|---|
| P3-3.4-001 | SIS user creation provisions a Moodle user. | Step 3.2 env vars are set; mocked Moodle REST or optional live Moodle token is available. | Create an active SIS student user. | Trigger `USER_SYNC_REQUESTED` or run `python manage.py process_moodle_sync`. | `MoodleUserMap` exists and Moodle receives `core_user_create_users` plus lookup. | Automated mocked; optional manual live. | Setup guide Step 3.4.1; `MI-A-003`, `MI-A-005`. | If live Moodle fails, check `MOODLE_WS_TOKEN`, `core_user_create_users`, and user-create capability. |
| P3-3.4-002 | SIS course section provisions a Moodle course shell. | Step 3.2 category env is set. | Create an active SIS course section. | Trigger `COURSE_SYNC_REQUESTED` or process outbox. | `MoodleCourseMap` exists and Moodle receives `core_course_create_courses`. | Automated mocked; optional manual live. | `MI-A-007`, `MI-A-009`. | Verify `MOODLE_DEFAULT_CATEGORY_ID` and category-level course-create permission. |
| P3-3.4-003 | SIS enrollment syncs into Moodle enrollment. | Moodle user/course maps exist. | Create student, section, and enrollment. | Process `ENROLLMENT_SYNC_REQUESTED`. | Moodle receives `enrol_manual_enrol_users` with student role ID, Moodle user ID, and course ID. | Automated mocked; optional manual live. | Setup guide Step 3.4.2; `FR-ENR-005`, `MI-A-010`. | If role is wrong, confirm `MOODLE_STUDENT_ROLE_ID` in Moodle role definitions. |
| P3-3.4-004 | Official numeric grade has Moodle grade pass-back foundation. | Moodle user/course maps exist; course map has explicit grade target metadata. | Create an official numeric grade record. | Process `GRADE_SYNC_REQUESTED`. | Moodle grade item lookup runs, then `core_grades_update_grades` runs with the configured target. | Automated mocked; optional manual live. | Setup guide Step 3.4.3; `FR-GRD-006`, `MI-A-013`, `MI-A-014`. | Step 3.4 does not guess gradebook targets. Fill `grade_component`, `grade_activity_id`, and `grade_item_number`. |
| P3-3.4-005 | Moodle course launch opens mapped SIS advising dashboard context. | Step 3.3 LTI env and mappings exist. | Create advisor/faculty user map, course map, section roster. | Launch `/lti/tools/advising-dashboard` through mocked LTI or optional Moodle external tool. | Protected context includes mapped SIS user, course section, roster, and safe launch identity. | Automated mocked; optional manual live. | Setup guide Step 3.4.4; `MI-B-004`, `MI-B-006`, `MI-B-007`. | If context is unmapped, run Lane A sync and inspect `MoodleUserMap` / `MoodleCourseMap`. |
| P3-3.4-006 | Advising dashboard supports student selection and engagement display. | LTI advising context includes a roster. | Add at least one `MoodleEngagementSnapshot` for a roster student. | Open the advising tool and select a roster student. | The selected-student panel shows SIS identity and latest Moodle engagement values or a safe no-snapshot state. | Automated frontend unit; automated backend mocked. | `MI-B-007`, `FR-STU-006`. | This is read-only. It is not the Phase 3.5 dashboard and does not generate at-risk alerts. |
| P3-3.4-007 | Moodle course launch opens mapped SIS registration context. | Step 3.3 LTI env and student mapping exist. | Create mapped student and active enrollment. | Launch `/lti/tools/registration` through mocked LTI or optional Moodle external tool. | Protected context includes mapped student and current SIS enrollments. | Automated mocked; optional manual live. | `MI-B-009`, `MI-B-010`. | Registration remains read-oriented in this slice; iframe mutations are not added here. |
| P3-3.4-008 | Moodle engagement ETL stores snapshots in SIS analytics tables. | `MOODLE_BASE_URL`, `MOODLE_WS_TOKEN`, user maps, and course maps exist. | Mock `core_enrol_get_enrolled_users` with `lastaccess` / `lastcourseaccess`. | Run `python manage.py ingest_moodle_engagement`. | A `MoodleEngagementIngestionRun` and `MoodleEngagementSnapshot` are created with mapped SIS user/student/section links. | Automated mocked; optional manual live. | Setup guide Step 3.4.5; `MI-A-012`, `MI-A-015`. | Assignment, quiz, and forum metrics are nullable until a later analytics expansion. |
| P3-3.4-009 | ETL dry run inspects Moodle without writing snapshots. | Same as P3-3.4-008. | Mock enrolled users. | Run `python manage.py ingest_moodle_engagement --dry-run`. | Run status is `DRY_RUN`; no snapshots are created. | Automated mocked. | Step 3.4 verification safety. | Use this before a live Moodle run to confirm scope and mappings. |
| P3-3.4-010 | ETL handles missing Moodle config safely. | No `MOODLE_BASE_URL` or no `MOODLE_WS_TOKEN`. | None. | Run service or command. | Command fails with a config error and no snapshots are created. | Automated mocked. | `MI-A-001`, `NFR-SEC-009`. | Export env vars explicitly; `.env.local` is not auto-loaded by Django. |
| P3-3.4-011 | ETL handles Moodle HTTP failure safely. | Moodle settings present. | Mock HTTP 500. | Run ingestion. | Run status is `FAILED`, failure count increments, and token is absent from errors. | Automated mocked. | `NFR-AVL-002`, secret safety. | Check Moodle container health and service-token permissions for live failures. |
| P3-3.4-012 | ETL handles Moodle exception payload safely. | Moodle settings present. | Mock a Moodle `exception` response. | Run ingestion. | Run status is `FAILED`, safe Moodle exception text is stored, and token is not leaked. | Automated mocked. | Moodle REST failure handling. | Common cause: function not added to the custom external service. |
| P3-3.4-013 | ETL handles invalid JSON safely. | Moodle settings present. | Mock non-JSON response. | Run ingestion. | Run status is `FAILED` with a safe invalid-JSON error. | Automated mocked. | Moodle REST failure handling. | Live cause can be a proxy or Moodle PHP error page. Inspect Moodle logs, not SIS token output. |
| P3-3.4-014 | Unmapped Moodle users are skipped safely. | Course map exists; matching user map is absent. | Mock enrolled user with unknown Moodle user ID. | Run ingestion. | `skipped_unmapped_users` increments and no orphan personal snapshot is created. | Automated mocked. | Privacy and mapping safety. | Run Lane A user sync before expecting snapshots for a live Moodle user. |
| P3-3.4-015 | Invalid or missing LTI launch context remains protected. | Step 3.3 LTI tests available. | Missing cookie, invalid JWT, replayed state, or wrong tool parameter. | Run LTI test suite. | API returns 401/403 as appropriate and does not expose SIS data. | Automated mocked. | `NFR-SEC-004`, `MI-B-004`. | Check key IDs, issuer allowlist, client ID, deployment ID, and state/nonce expiry. |
| P3-3.4-016 | Unmapped Moodle user/course launch gives limited context. | Valid LTI launch but no mapping records. | Launch with Moodle IDs not in maps. | Request `/lti/api/session`. | Response is valid but `isMapped=false`, with no roster/student SIS data. | Automated mocked; optional manual live. | Mapping safety. | This is expected until Step 3.2 provisioning has created maps. |
| P3-3.4-017 | Secret-safety checks cover tokens and key material. | Tests and docs are present. | Use placeholder tokens and generated test keys. | Run integration and LTI tests; inspect output. | No real Moodle token, private key, or launch JWT appears in errors, docs, snapshots, or command output. | Automated mocked plus manual review. | `NFR-SEC-009`. | Keep `local-secrets/`, `.env.local`, private keys, and real tokens untracked. |
| P3-3.4-018 | Automated tests do not require live Moodle. | Normal development environment. | None. | Run backend and frontend checks without starting Moodle. | Mocked tests pass without live Moodle network calls. | Automated. | CI reliability. | Live Moodle is reserved for optional verification below. |
| P3-3.4-019 | Optional live Moodle verifies end-to-end Step 3.4 flow. | Moodle overlay running; service token and LTI tool configured. | Use local SIS demo/test student, section, enrollment, grade, and external tool. | Run REST verification, process sync, ingest engagement, then launch LTI tools from Moodle. | Moodle reflects SIS provisioning and SIS stores engagement snapshots; LTI pages load mapped context. | Manual optional. | Setup guide Step 3.4.1-3.4.6. | Use the runbook in the Phase 3 README. Do not commit tokens or keys. |
| P3-3.4-020 | Readiness command reports local integration state without live Moodle. | Django env is loaded. | Optional mappings, outbox events, and ingestion runs exist. | Run `python manage.py verify_phase_3_integrations`. | Output reports config presence, mapping counts, pending/failed outbox counts, latest ingestion run, and says live Moodle calls were not performed. | Automated mocked; manual useful. | Step 3.4 verification helper. | This is a checklist report, not a monitoring dashboard. |

## Optional Live Moodle Verification

Live Moodle is not required for CI or normal local automated tests. When you do want live confidence:

```bash
docker compose \
  --env-file infra/moodle.env.example \
  -f infra/docker-compose.yml \
  -f infra/docker-compose.moodle.yml \
  --profile later-phase \
  up -d moodle_db moodle
```

In Moodle admin, make sure the custom service includes the Step 3.2 functions plus Step 3.4 `core_enrol_get_enrolled_users`. Then export local env values and run:

```bash
cd backend
python manage.py verify_moodle_rest
python manage.py process_moodle_sync --failed
python manage.py ingest_moodle_engagement --dry-run
python manage.py ingest_moodle_engagement
python manage.py verify_phase_3_integrations
```

Inspect snapshots in Django shell if needed:

```bash
python manage.py shell -c "from apps.integration.models import MoodleEngagementSnapshot; print(MoodleEngagementSnapshot.objects.count())"
```

For LTI live launch checks, use the Step 3.3 testing guide and confirm both:

- `/lti/tools/advising-dashboard` loads mapped course, roster, and student selection.
- `/lti/tools/registration` loads mapped student and current enrollment context.
