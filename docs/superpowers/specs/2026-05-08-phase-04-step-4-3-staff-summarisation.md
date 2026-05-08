# Step 4.3 — Staff Workflow Acceleration (Summarisation) Design

**Date:** 2026-05-08
**Phase:** 4
**SRS Reference:** Section 6.2 (AI-SUM-001 through AI-SUM-007)
**Setup Guide Reference:** Phase 4 Step 4.3
**Depends on:** Step 4.2 (co-pilot provider pattern, AIAuditLog, OpenAI-compatible infrastructure)

---

## Purpose

Reduce the time advisors and admin staff spend writing structured records from unstructured notes, without removing human accountability from any official record.

---

## Scope

**In scope:**
- `POST /api/v1/ai/summarise/` endpoint returning structured JSON summary
- `POST /api/v1/ai/summarise/approve/` endpoint saving human-approved version as official advising note
- Deterministic provider for tests and CI (no paid API required)
- OpenAI-compatible provider for live use (reuses existing AI_PROVIDER configuration)
- Full AI audit logging (raw input, AI output, human-edited final, approving user, student ID, timestamp)
- Live `AISummarisationPanel` replacing the existing disabled placeholder in advisor student profile
- Standalone `/admin/summarise` page for admin staff without student context
- Demo seed data and management commands
- Five real-world-style advising scenario test cases

**Out of scope:**
- At-risk scoring, wellbeing workflows, co-pilot changes
- Batch summarisation or file upload
- Automatic summarisation triggers
- Summarisation of student documents or Moodle content
- Changes to existing advising note CRUD beyond the approve-from-summary flow

---

## SRS Requirements Mapping

| ID | Requirement | Implementation |
|---|---|---|
| `AI-SUM-001` | Accessible only to advisor or admin role | Backend permission class + frontend route guards |
| `AI-SUM-002` | Accept up to 5,000 characters with truncation warning | Frontend char counter + backend validation |
| `AI-SUM-003` | Structured JSON with `key_issues`, `recommended_actions`, `urgency_level` | Provider prompt + response parsing + validation |
| `AI-SUM-004` | Render editable form, not raw JSON | Frontend editable summary form component |
| `AI-SUM-005` | Approve & Save requires explicit button click, not auto-save | Explicit button with confirmation state |
| `AI-SUM-006` | Log raw input, AI output, final saved text, user ID, student ID, timestamp | `AIAuditLog` records via existing copilot audit model |
| `AI-SUM-007` | Display governance notice above input | Static notice banner in UI |

---

## Backend Design

### New App: `apps.summarisation`

```
backend/apps/summarisation/
├── __init__.py
├── apps.py
├── models.py          # SummarisationRequest record
├── providers.py       # Deterministic + OpenAI-compatible providers
├── prompts.py         # Structured extraction prompt
├── serializers.py     # Input/output serializers
├── services.py        # Orchestration: validate → call provider → audit
├── permissions.py     # IsAdvisorOrAdmin
├── urls.py
├── views.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_services.py
└── management/
    └── commands/
        ├── __init__.py
        └── seed_summarisation_demo.py
```

### Models

```python
class SummarisationRequest(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(AUTH_USER_MODEL)          # requesting advisor/admin
    student = ForeignKey(StudentProfile, null=True, blank=True)  # optional student context
    raw_input_text = TextField()                # original pasted text
    ai_output = JSONField()                     # { key_issues, recommended_actions, urgency_level }
    human_edited_output = JSONField(null=True)  # final approved version (null until approved)
    advising_note = ForeignKey(AdvisingNote, null=True, blank=True)  # linked note after approval
    status = CharField(choices=[PENDING, APPROVED, DISCARDED])
    provider = CharField()                      # deterministic or openai_compatible
    model_name = CharField()
    latency_ms = IntegerField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    approved_at = DateTimeField(null=True)
```

### API Endpoints

| Method | Path | Purpose | Auth |
|---|---|---|---|
| `POST` | `/api/v1/ai/summarise/` | Submit text, receive structured summary | Advisor or Admin |
| `POST` | `/api/v1/ai/summarise/{id}/approve/` | Save human-edited version as official record | Advisor or Admin |

### Provider Design

Reuses the same pattern as `apps.copilot.providers`:

- **DeterministicSummarisationProvider**: extracts keyword-based mock summary for tests/CI
- **OpenAISummarisationProvider**: sends structured extraction prompt to OpenAI-compatible endpoint

Both return:
```python
@dataclass
class SummarisationResult:
    key_issues: list[str]
    recommended_actions: list[str]
    urgency_level: str  # "Routine" | "Follow-up Needed" | "Urgent"
    provider: str
    model_name: str
    metadata: dict
```

### Prompt (for OpenAI-compatible provider)

```
You are an academic advising assistant. Extract a structured summary from the following raw advising notes.

Return ONLY valid JSON with exactly these fields:
- "key_issues": array of 1-5 concise issue descriptions
- "recommended_actions": array of 1-5 specific next steps
- "urgency_level": exactly one of "Routine", "Follow-up Needed", or "Urgent"

Do not invent information not present in the input. Do not include student names or IDs in the output.
```

### Audit Logging

Every summarisation request writes an `AIAuditLog` record (reuses the existing model from `apps.copilot`) with:
- `action`: `SUMMARISATION_REQUEST` or `SUMMARISATION_APPROVED`
- `input_text`: raw input (redacted to safe length)
- `output_text`: AI JSON output
- `metadata`: includes `humanEditedOutput` on approval
- `user`, `student` (optional), `provider`, `model_name`, timestamp

Also writes a safe `AuditEvent` via `apps.audit` for the activity trail.

---

## Frontend Design

### 1. Live AISummarisationPanel (advisor student profile)

Replaces the existing disabled placeholder at `frontend/src/components/advisor/AISummarisationPanel.tsx`.

**States:**
1. **Input** — textarea (max 5000 chars with counter), governance notice, "Generate summary" button
2. **Loading** — thinking indicator while API processes
3. **Review** — editable form with key_issues (editable list), recommended_actions (editable list), urgency_level (select dropdown), "Approve & Save" button, "Discard" button
4. **Success** — confirmation that the approved note was saved
5. **Error** — retryable error state

### 2. Standalone Admin Summarise Page (`/admin/summarise`)

Same component logic but without student context. Approved summaries are stored as `SummarisationRequest` records (no `AdvisingNote` created since there's no student binding). Accessible from admin sidebar.

### Hook

```typescript
// frontend/src/hooks/useSummarisation.ts
useSummarisationMutation()    // POST /api/v1/ai/summarise/
useApproveSummarisationMutation(id)  // POST /api/v1/ai/summarise/{id}/approve/
```

---

## Demo Data

`python manage.py seed_summarisation_demo` creates:
- 3-5 pre-seeded summarisation requests with example advising scenarios
- At least 2 approved examples showing the full flow
- Uses existing demo advisor user and demo students

---

## Test Scenarios (Setup Guide requirement: 5 real-world advising scenarios)

1. **Academic probation meeting** — student struggling in multiple courses, advisor discusses study plan
2. **Course withdrawal discussion** — student wants to drop a course past deadline, financial implications
3. **Graduate school preparation** — student seeking recommendation letter guidance and research opportunities
4. **Personal circumstances** — student requesting extension due to family emergency (no wellbeing data)
5. **Internship credit approval** — advisor reviewing whether work placement qualifies for academic credit

---

## Governance Boundaries

- Raw AI output is never stored as an official `AdvisingNote` — only human-approved version
- Input capped at 5,000 characters with frontend and backend validation
- No wellbeing data, no student documents, no Moodle content processed
- No SIS mutations beyond creating the approved advising note
- Provider credentials never logged in audit records
- Deterministic provider available for all tests — no paid API needed for CI
