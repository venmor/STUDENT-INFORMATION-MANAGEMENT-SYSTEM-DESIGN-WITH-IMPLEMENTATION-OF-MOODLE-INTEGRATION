# UI/UX Overhaul & Feature Completion Specification

**Version:** 1.0
**Date:** 2026-05-11
**Status:** Ready for Implementation
**SRS Alignment:** v2.2

---

## 1. Purpose

This document specifies the remaining UI/UX improvements and feature gaps required to bring the Modern SIS from its current functional-but-incomplete state to a polished, production-ready university platform. Every change traces back to the Software Requirements Specification (SRS v2.2) or to an explicit usability gap identified during review.

The implementing agent should treat this document as the authoritative work plan and reference the SRS (`docs/project/SRS_Modern_SIS.md`) and Setup Guide (`docs/project/modern-sis-setup-guide.md`) for full requirement text.

---

## 2. Current Implementation State

### 2.1 Technology Stack (Confirmed)

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Python 3.11+ / Django 5.2 / Django REST Framework 3.16 | Confirmed in `backend/requirements/base.txt` |
| Frontend | React 18.3 / TypeScript 6.0 / Vite 8.0 | Confirmed in `frontend/package.json` |
| Styling | Tailwind CSS 3.4 with custom palette (Primary #1E4E8C, Secondary #0D9488) | Confirmed in `frontend/tailwind.config.js` |
| State Management | Zustand (auth), TanStack React Query 5.x (server state) | Confirmed in `frontend/package.json` |
| UI Primitives | Radix UI (dialog, select, popover, tabs, tooltip), Heroicons | Confirmed in `frontend/package.json` |
| Database | MySQL 8.0 | Confirmed in `infra/docker-compose.yml` |
| API Client | Axios with interceptors | Confirmed in `frontend/src/api/axios.ts` |
| Fonts | DM Sans (body), Sora (display), JetBrains Mono (mono) | Confirmed in `tailwind.config.js` |
| Icons | @heroicons/react 2.2 | Confirmed |
| Testing | Vitest + React Testing Library (unit), Playwright (E2E) | Confirmed |

### 2.2 Implemented Backend Apps (14 apps, 54 models)

| App | Models | Status |
|-----|--------|--------|
| `apps.accounts` | User, Role, UserCapability, AccessLog | Complete |
| `apps.academics` | Course, CoursePrerequisite, CourseSection, SectionTimetable, Enrollment, EnrollmentEvent, WaitlistEntry, AttendanceSession, AttendanceRecord, GradingScaleBand, AcademicStandingRule, GradeRecord, GradeChangeLog | Complete |
| `apps.students` | StudentProfile, AdvisorAssignment, FinancialFlag, AdvisingNote, StudentCorrectionRequest | Complete |
| `apps.integration` | IntegrationOutboxEvent, MoodleUserMap, MoodleCourseMap, MoodleEngagementIngestionRun, MoodleEngagementSnapshot, LtiOidcState, LtiLaunchSession | Complete |
| `apps.notifications` | Notification | Complete |
| `apps.audit` | AuditEvent | Complete |
| `apps.calendar` | AcademicCalendarEvent | Complete |
| `apps.documents` | StudentDocument | Complete |
| `apps.analytics` | AnalyticsETLRun, StudentAnalyticsSnapshot | Complete |
| `apps.knowledge` | KnowledgeSource, KnowledgeChunk, KnowledgeIngestionRun | Complete |
| `apps.copilot` | CopilotSession, CopilotMessage, AIAuditLog, CopilotFeedback | Complete |
| `apps.summarisation` | SummarisationRequest | Complete |
| `apps.atrisk` | AtRiskAlert | Complete |
| `apps.wellbeing` | WellbeingConsent, WellbeingCheckIn, WellbeingAuditLog | Complete |
| `apps.reporting` | (no models — services only) | Complete |

### 2.3 Implemented Frontend Pages (30 pages)

| Route | Page | Role |
|-------|------|------|
| `/login` | Login | Public |
| `/student/dashboard` | Student Dashboard | Student |
| `/student/courses` | My Courses | Student |
| `/student/grades` | My Grades | Student |
| `/student/registration` | Course Registration | Student |
| `/student/copilot` | AI Co-pilot | Student |
| `/student/corrections` | Correction Requests | Student |
| `/student/wellbeing` | Wellbeing Check-in | Student |
| `/documents` | Student Documents | Student |
| `/advisor/dashboard` | Advisor Dashboard | Advisor |
| `/advisor/students/:id` | Student Profile | Advisor |
| `/advisor/alerts/history` | Alert History | Advisor |
| `/faculty/dashboard` | Faculty Dashboard | Faculty |
| `/faculty/sections/:id` | Section Detail | Faculty |
| `/admin/dashboard` | Admin Dashboard | Admin |
| `/admin/users` | User Management | Admin |
| `/admin/courses` | Course Management | Admin |
| `/admin/moodle-sync` | Moodle Sync Monitoring | Admin |
| `/admin/audit-log` | Audit/Activity Viewer | Admin |
| `/admin/reports` | Reports Dashboard | Admin |
| `/admin/documents` | Document Management | Admin |
| `/admin/ai-foundation` | AI Foundation | Admin |
| `/admin/summarise` | Summarisation Tool | Admin |
| `/notifications` | Notification Center | All Roles |
| `/calendar` | Academic Calendar | All Roles |
| `/account/password` | Password Change | All Roles |
| `/lti/tools/advising-dashboard` | LTI Advising Tool | LTI |
| `/lti/tools/registration` | LTI Registration Tool | LTI |

### 2.4 API Layer (18 API modules in `frontend/src/api/`)

All CRUD operations and queries are wired through Axios with JWT Bearer interceptors.

### 2.5 Existing Management Commands (20 commands)

Covering demo seeding, ETL processing, Moodle sync, knowledge ingestion, copilot testing, at-risk engine, and integration verification.

---

## 3. Gap Analysis & Work Items

### 3.1 PRIORITY 0 — Critical UI/UX Foundation

These items address SRS Section 4.5 (Usability) and 4.7 (Accessibility) requirements.

#### 3.1.1 Layout & Navigation (NFR-USE-002)

**Current state:** Sidebar scrolls with page content; horizontal scrollbars appear on narrow viewports.

**Required changes:**
- Make the sidebar (`frontend/src/components/layout/Sidebar.tsx`) `position: fixed` or `sticky` with independent `overflow-y: auto`.
- Set the main content area to `overflow-x: hidden` with a max-width container.
- The `AppShell.tsx` must use a CSS grid or flex layout that prevents horizontal overflow at all breakpoints down to 375px.
- Mobile: sidebar becomes a slide-out drawer (the `MobileNav.tsx` component exists — verify it works correctly).

**Files to modify:** `Sidebar.tsx`, `AppShell.tsx`, `MobileNav.tsx`

#### 3.1.2 Interactive States & Feedback (NFR-USE-003, NFR-USE-004)

**Current state:** Buttons lack loading states, success/error toasts are absent, tabs appear non-interactive.

**Required changes:**
- Create a global toast notification system (use Radix Toast or a lightweight custom hook). Mount it in `AppShell.tsx`.
- Wrap every mutation (form submit, approve, reject, delete, sync) in a loading state using React Query's `useMutation` with `isPending` → show spinner on button, `onSuccess` → show success toast, `onError` → show error toast with message from API response.
- Add `cursor-pointer`, `hover:bg-*`, `focus-visible:ring-*`, and `active:scale-95` to all interactive elements via a shared Tailwind utility class.
- Ensure all `<button>` and `<a>` elements that navigate or mutate have appropriate ARIA labels.

**Files to modify:** All page and component files containing buttons/forms. Create `frontend/src/components/ui/Toast.tsx` and a `useToast` hook.

#### 3.1.3 Admin Table Enhancements (FR-USR-008)

**Current state:** Admin tables (users, courses) have no search, sort, or filter capabilities.

**Required changes:**
- Add a live search bar (debounced, 300ms) at the top of every admin data table.
- Add sortable column headers (click to sort asc/desc, visual indicator arrow).
- Add dropdown filters for key fields (role, status, programme).
- These can be implemented as enhancements to the existing `Table.tsx` component or as a new `DataTable.tsx` wrapper.

**Files to modify:** `frontend/src/components/ui/Table.tsx`, `frontend/src/pages/admin/Users.tsx`, `frontend/src/pages/admin/Courses.tsx`

#### 3.1.4 Dashboard Widget Navigation (FR-STU-005)

**Current state:** Dashboard cards/widgets are static and non-clickable.

**Required changes:**
- Every dashboard widget (student: My Courses, My Grades, Notifications, Wellbeing; advisor: Advisees, At-Risk Alerts, Notes; admin: Users, Sync Status, Reports) must be clickable and navigate to the relevant detail page.
- Use `<Link>` wrapper or `onClick` with `useNavigate`.
- Visual affordance: add `hover:shadow-md`, `transition-shadow`, and `cursor-pointer` to clickable cards.

**Files to modify:** All `Dashboard.tsx` files and their child widget components.

#### 3.1.5 Calendar Event Detail View (FR-OPS-004)

**Current state:** Calendar events are not clickable; no detail view exists.

**Required changes:**
- On clicking a calendar event, open a Radix Dialog (modal) showing full event details: title, description, dates, type, audience, location, priority, and related course section.
- If the event type is `EXAM_PERIOD`, display a link to the student's exam schedule or document section.

**Files to modify:** `frontend/src/pages/AcademicCalendar.tsx`

#### 3.1.6 Tooltips & Help Text (NFR-USE-001)

**Current state:** No tooltips or help text on ambiguous UI elements.

**Required changes:**
- Use Radix Tooltip (already in dependencies as `@radix-ui/react-tooltip`) to add hover explanations to:
  - Status badges (Academic Standing, Enrollment Status, Grade Status)
  - Action icons (edit, delete, approve, reject)
  - Section concept: "A section is a specific class group of a course with its own timetable and instructor."
  - Capability badges (wellbeing_coordinator)
- Create a reusable `<Tooltip>` wrapper in `frontend/src/components/ui/Tooltip.tsx`.

**Files to modify:** Create `Tooltip.tsx`, apply throughout pages.

#### 3.1.7 AI Co-pilot UI Redesign (NFR-USE-006, AI-COP-001)

**Current state:** The copilot feature directory (`frontend/src/features/copilot/`) has 12 components. The chat interface exists but reportedly looks dated.

**Required changes:**
- The `CopilotChatShell.tsx` should use a modern split layout: collapsible session list on the left, main chat area center, source/citation panel on the right (collapsible).
- Messages should have clear visual distinction: user messages right-aligned in primary colour, assistant messages left-aligned with a subtle card.
- The `CopilotSourcePanel.tsx` should show source document title, chunk preview, and confidence badge (HIGH = green, MEDIUM = amber, LOW = red).
- The persistent disclaimer (AI-COP-006) must remain visible at all times.
- Connect to the actual RAG pipeline by ensuring `AI_PROVIDER` environment variable is set to `openai_compatible` in production. The deterministic provider is for CI only.

**Files to modify:** `frontend/src/features/copilot/components/CopilotChatShell.tsx` and siblings. No backend changes needed — the backend already supports both providers.

---

### 3.2 PRIORITY 0 — Academic Hierarchy (FR-CRS-003)

#### 3.2.1 New Backend Models

**Current state:** The `Course` model has `department` (CharField) and `programme_code` (CharField) as flat text fields. There is no hierarchical structure.

**Required new models** (create in a new app `apps.structure` or extend `apps.academics`):

```python
class School(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=10, unique=True)  # e.g., "SoNHAS"
    name = models.CharField(max_length=200)  # e.g., "School of Natural and Health Applied Sciences"
    is_active = models.BooleanField(default=True)

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=10, unique=True)  # e.g., "CS"
    name = models.CharField(max_length=200)  # e.g., "Department of Computer Science"
    school = models.ForeignKey(School, CASCADE, related_name="departments")
    is_active = models.BooleanField(default=True)

class Programme(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=20, unique=True)  # e.g., "BSc-CS"
    name = models.CharField(max_length=200)  # e.g., "Bachelor of Science in Computer Science"
    department = models.ForeignKey(Department, CASCADE, related_name="programmes")
    level = models.CharField(choices=[("UG","Undergraduate"),("PG","Postgraduate")])
    duration_years = models.PositiveSmallIntegerField(default=4)
    is_active = models.BooleanField(default=True)

class Stream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=20, unique=True)  # e.g., "CS-SE"
    name = models.CharField(max_length=200)  # e.g., "Software Engineering"
    programme = models.ForeignKey(Programme, CASCADE, related_name="streams")
    is_active = models.BooleanField(default=True)
```

**Relationships to existing models:**
- `Course.department` (CharField) → Replace with `Course.department` (FK → Department) or add a new `Course.programme` FK field. To maintain backwards compatibility, add nullable FK fields alongside existing CharFields and migrate data.
- `StudentProfile.programme` (CharField) → Add a nullable `StudentProfile.programme_ref` FK → Programme. Existing text field remains for display until data is migrated.
- Add `CourseSection.stream` (FK → Stream, nullable) to indicate stream-specific sections.

**API endpoints:**
- `GET /api/v1/structure/schools` — list all schools
- `GET /api/v1/structure/departments` — list departments (filter by school)
- `GET /api/v1/structure/programmes` — list programmes (filter by department, level)
- `GET /api/v1/structure/streams` — list streams (filter by programme)
- Admin CRUD for all four entities.

**Frontend changes:**
- Course catalog (`/admin/courses`) shows a hierarchical sidebar: School → Department → Programme → Courses.
- Student registration (`/student/registration`) filters available courses by the student's programme, year, and stream.
- Admin can create/edit schools, departments, programmes, and streams from a new `/admin/academic-structure` page.

---

### 3.3 PRIORITY 1 — Admissions & Applicant Intake (Step 3.5G)

**SRS Reference:** `FR-ADM-001` (optional/future, now being implemented)

#### 3.3.1 Backend Models

Create `apps.admissions`:

```python
class ApplicantProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    national_id = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    programme_applied = models.ForeignKey("academics.Programme", SET_NULL, null=True)
    application_status = models.CharField(choices=[
        ("DRAFT","Draft"),("SUBMITTED","Submitted"),
        ("UNDER_REVIEW","Under Review"),("ACCEPTED","Accepted"),
        ("REJECTED","Rejected"),("WAITLISTED","Waitlisted")
    ], default="DRAFT")
    review_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, SET_NULL, null=True)
    reviewed_at = models.DateTimeField(null=True)
    converted_user = models.OneToOneField(User, SET_NULL, null=True, related_name="applicant_source")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ApplicantDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    applicant = models.ForeignKey(ApplicantProfile, CASCADE)
    document_type = models.CharField(choices=[...])
    file = models.FileField(upload_to="applicant_docs/%Y/%m/")
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

#### 3.3.2 Workflow

1. Public application form at `/apply` (unauthenticated route).
2. Applicant submits profile + required documents → status = SUBMITTED.
3. Admin review queue at `/admin/admissions` shows submitted applications.
4. Admin can approve → triggers: User creation, StudentProfile creation, acceptance letter PDF generation (via reportlab), and notification to applicant email.
5. Acceptance letter stored in `StudentDocument` with type `ADMISSION_LETTER`.

#### 3.3.3 Frontend Pages

- `/apply` — Public multi-step application form (personal details, programme selection, document upload, review & submit).
- `/admin/admissions` — Admin queue with filters (status, programme), detail view, approve/reject actions.

---

### 3.4 PRIORITY 1 — Registration Workflow with Approval (FR-ENR-001, FR-ENR-003)

**Current state:** The existing `Enrollment` model supports `ENROLLED`, `DROPPED`, `WAITLISTED`, `TRANSFERRED` statuses. Self-enrollment is instant with no approval step.

#### 3.4.1 Backend Changes

Add a new status to the `Enrollment.enrollment_status` choices:
- `PENDING_APPROVAL` — submitted by student, awaiting advisor/HOD review.

Add fields to `Enrollment`:
- `approval_required` (BooleanField, default=False)
- `approved_by` (FK → User, nullable)
- `approved_at` (DateTimeField, nullable)

New API endpoints:
- `GET /api/v1/advisor/registrations/pending` — list pending registrations for advisor's advisees.
- `POST /api/v1/advisor/registrations/{enrollment_id}/approve`
- `POST /api/v1/advisor/registrations/{enrollment_id}/reject`

#### 3.4.2 Workflow

1. Student selects courses from programme-filtered catalog.
2. Compulsory courses for the student's programme/year/stream are pre-selected.
3. Electives shown from allowed baskets based on programme rules.
4. On submit: enrollments created with `PENDING_APPROVAL` status.
5. Advisor receives notification, reviews in their dashboard.
6. On approval: status changes to `ENROLLED`, Moodle sync triggered, confirmation slip generated.
7. On rejection: student notified with reason, can re-submit.
8. After drop deadline (`CourseSection.drop_deadline`), drops require advisor approval.

#### 3.4.3 Frontend Changes

- Redesign `/student/registration` as a multi-step wizard:
  - Step 1: Select stream (if applicable).
  - Step 2: View pre-selected compulsory courses + choose electives.
  - Step 3: Review selections.
  - Step 4: Submit for approval.
- Add `/advisor/registrations` page showing pending approvals.
- Generate confirmation slip PDF on successful enrollment (store in student documents).

---

### 3.5 PRIORITY 2 — Grade Management Enhancements (FR-GRD-001, FR-STU-008)

**Current state:** `GradeRecord` stores a single `numeric_score` (0-100), `letter_grade`, `grade_points`, and status (DRAFT/OFFICIAL). No CA/Exam breakdown or pass/fail logic exists in the frontend.

#### 3.5.1 Backend Changes

The SRS mandates a single numeric grade (0-100). The CA/Exam breakdown is a **UI convenience** that sums to the stored score. Add to `GradeRecord`:
- `ca_score` (DecimalField 5,2, nullable) — Continuous Assessment component
- `exam_score` (DecimalField 5,2, nullable) — Examination component

These are informational; the `numeric_score` remains the official stored value.

Add pass/fail logic as a service function:
```python
def determine_academic_outcome(student, semester, academic_year):
    """Based on configurable thresholds:
    - Pass: grade >= C (configurable via GradingScaleBand.is_passing)
    - Supplementary: fail <= 2 courses
    - Repeat: fail > 2 courses
    """
```

#### 3.5.2 Frontend Changes

- Group grades by semester/year in `/student/grades` with per-semester GPA.
- Show CA + Exam columns alongside total score.
- Display pass/fail indicators and academic outcome (Clear, Supplementary, Repeat).
- Faculty grade entry: add "Download Template" (CSV with student names/IDs) and "Upload Grades" (CSV with validation preview).
- Generate exam slip and results slip PDFs:
  - Exam slip: generated when exam period calendar event is active, lists courses, dates, venues.
  - Results slip: generated after grades are officialised, shows CA/exam/total/GPA.
  - Both stored via `StudentDocument` and visible in `/documents`.

---

### 3.6 PRIORITY 3 — Advisor & Faculty Tools

#### 3.6.1 Advising Notes Fix (FR-STU-019, FR-STU-020)

**Current state:** `AdvisingNote` model supports DRAFT → APPROVED workflow. The `AdvisingNoteEditor.tsx` component exists.

**Required fixes:**
- Verify the advisor can create a draft note, edit it, and submit for approval.
- Admin can approve/reject draft notes.
- Show approval status clearly in the notes list.
- Integrate with the AI summarisation panel (`AISummarisationPanel.tsx`).

#### 3.6.2 Role Switching (FR-USR-005, FR-USR-004)

**Current state:** Each user has one `primary_role`. Some users (e.g., a faculty member who is also an advisor) need to switch contexts.

**Required change:**
- Allow users to hold multiple roles by adding a `secondary_roles` M2M field or by using the existing `UserCapability` mechanism.
- In the Sidebar, show a role context selector if the user has multiple applicable roles.
- Switching roles changes the sidebar menu and dashboard without requiring re-authentication.

#### 3.6.3 Admin Impersonation

**Required change:**
- Admin can "View As" any user (read-only).
- When active: a prominent warning banner shows "Viewing as [username] — Read Only".
- All actions are blocked; only read endpoints are accessible.
- Audit logged with full metadata.

---

### 3.7 PRIORITY 3 — Wellbeing Enhancement (AI-WBE-002)

**Current state:** Check-in form collects mood (1-5) + optional text comment. Escalation notifications work.

**Required enhancement:**
- Allow optional file upload (medical note, supporting document) on the check-in form.
- Files stored in restricted wellbeing storage (separate from general documents).
- Only `wellbeing_coordinator` users can view uploaded files.
- Crisis contacts displayed immediately on ESCALATE classification (already implemented in `WellbeingEscalationScreen.tsx` — verify).

---

### 3.8 PRIORITY 3 — Moodle Integration Verification (MI-A-*, MI-B-*)

**Current state:** Sync is event-driven via `IntegrationOutboxEvent`. The admin monitoring dashboard (3.5A) exists.

**Required verification:**
- Confirm that all provisioning (user creation, enrollment, grade pass-back) fires automatically via the outbox processor without manual intervention.
- The admin Moodle Sync page should primarily show status/health, not require "Sync Now" buttons for normal operation.
- Verify LTI 1.3 launch flow works end-to-end (JWT validation, session creation, context mapping).
- If the sync is currently manual-only, add a periodic check (Celery beat when available, or a health check endpoint that processes pending outbox events).

---

## 4. Implementation Order

The implementing agent should follow this sequence:

| Step | Work Item | Priority | Estimated Complexity |
|------|-----------|----------|---------------------|
| 1 | Fix global layout (sticky sidebar, no horizontal scroll) | P0 | Low |
| 2 | Create Toast notification system and apply to all mutations | P0 | Medium |
| 3 | Add interactive states (hover/focus/loading) to all buttons and cards | P0 | Medium |
| 4 | Add search, sort, filter to admin tables | P0 | Medium |
| 5 | Make dashboard widgets clickable/navigable | P0 | Low |
| 6 | Add calendar event detail modal | P0 | Low |
| 7 | Create Tooltip component and apply where needed | P0 | Low |
| 8 | Implement Academic Hierarchy models (School, Dept, Programme, Stream) | P0 | High |
| 9 | Connect courses to programmes, update catalog filters | P0 | High |
| 10 | Redesign AI co-pilot chat interface | P0 | Medium |
| 11 | Build Admissions Pipeline (models, API, public form, admin queue) | P1 | High |
| 12 | Build Registration Approval Workflow | P1 | High |
| 13 | Enhance Grade Views (semester grouping, CA/Exam, pass/fail) | P2 | Medium |
| 14 | Add exam slip and results slip PDF generation | P2 | Medium |
| 15 | Add faculty batch grade template (download/upload CSV) | P2 | Medium |
| 16 | Fix advising notes workflow | P3 | Low |
| 17 | Add role switching for multi-role users | P3 | Medium |
| 18 | Add admin impersonation (read-only) | P3 | Medium |
| 19 | Add wellbeing file upload support | P3 | Low |
| 20 | Verify Moodle sync automation | P3 | Low |

---

## 5. File Structure Guidance

### 5.1 New Backend App: `apps.structure`

```
backend/apps/structure/
├── __init__.py
├── apps.py
├── models.py          (School, Department, Programme, Stream)
├── serializers.py
├── views.py
├── urls.py
├── admin.py
├── migrations/
│   └── __init__.py
├── management/
│   └── commands/
│       └── seed_academic_structure.py
└── tests/
    └── test_structure.py
```

### 5.2 New Backend App: `apps.admissions`

```
backend/apps/admissions/
├── __init__.py
├── apps.py
├── models.py          (ApplicantProfile, ApplicantDocument)
├── serializers.py
├── views.py
├── urls.py
├── services.py        (acceptance workflow, PDF generation, account creation)
├── admin.py
├── migrations/
│   └── __init__.py
├── management/
│   └── commands/
│       └── seed_admissions_demo.py
└── tests/
    └── test_admissions.py
```

### 5.3 Frontend New Components

```
frontend/src/components/ui/
├── Toast.tsx          (global notification toast)
├── Tooltip.tsx        (Radix tooltip wrapper)
├── DataTable.tsx      (searchable, sortable, filterable table)
└── SearchInput.tsx    (debounced search input)

frontend/src/pages/admin/
├── AcademicStructure.tsx   (School/Dept/Programme/Stream CRUD)
└── Admissions.tsx          (Applicant review queue)

frontend/src/pages/public/
└── Apply.tsx               (Public application form)

frontend/src/pages/advisor/
└── PendingRegistrations.tsx (Registration approval queue)
```

---

## 6. Database Migration Strategy

All new models should:
1. Use `UUIDField` as primary key (consistent with all existing models).
2. Add new FK fields as **nullable** initially to avoid breaking existing data.
3. Provide a data migration to populate FK relationships from existing CharField values where applicable (e.g., `Course.department` text → `Course.department_ref` FK).
4. Keep existing CharField fields until all data is migrated and verified.

---

## 7. Testing Requirements

- Every new API endpoint must have at least one happy-path test and one permission-denial test.
- New frontend components must have Vitest unit tests.
- The existing test suite (258 backend tests at 89.65% coverage, 95 frontend tests) must continue to pass after all changes.
- Coverage must remain above 80% for backend.

---

## 8. Environment & Configuration

No new environment variables are required for the P0 and P1 work items. The AI co-pilot already supports both `deterministic` and `openai_compatible` providers via the existing `AI_PROVIDER` variable.

For production RAG usage, set:
```
AI_PROVIDER=openai_compatible
OPENAI_API_KEY=<key>
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

---

## 9. Acceptance Criteria

1. No page requires horizontal scrolling; sidebar remains fixed at all viewport widths.
2. Every data table has live search and at least one sort option.
3. All buttons/tabs perform an action with visual feedback (spinner on press, toast on complete).
4. A student can register, see programme-filtered courses, submit for advisor approval, and receive a confirmation slip.
5. Advisors see a meaningful dashboard with at-risk flags and can approve registrations and write notes.
6. Faculty can download and upload grade templates.
7. AI co-pilot answers questions with source citations when connected to a real LLM provider.
8. Wellbeing check-in supports file upload, with immediate escalation to coordinator.
9. All existing 258 backend and 95 frontend tests continue to pass.
10. Coverage remains above 80%.

---

## 10. References

- SRS: `docs/project/SRS_Modern_SIS.md` (v2.2)
- Setup Guide: `docs/project/modern-sis-setup-guide.md`
- Phase 6 Spec: `docs/phases/phase-06-wellbeing-support/README.md`
- Architecture: `docs/architecture/ADR-001-technology-baseline.md`
- OpenAPI: `docs/api/openapi.yaml`
- Existing Design Specs: `docs/superpowers/specs/`
