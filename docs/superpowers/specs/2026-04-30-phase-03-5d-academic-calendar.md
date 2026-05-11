# Phase 3.5D Academic Calendar And Deadline Rules Spec

## Status

Accepted for implementation on 2026-04-30.

## Scope

Step 3.5D adds a central Academic Calendar module for institutional dates and deadline rules. It is a tightly scoped operational-completion slice after Step 3.5C and before Step 3.5E.

This slice implements:

- A backend `AcademicCalendarEvent` model for academic dates, deadlines, event source, status, priority, audience, and optional course-section linkage.
- Authenticated calendar APIs under `/api/v1/calendar/`.
- Role-aware event visibility for students, faculty, advisors, and admins.
- Admin-only create, update, and cancel actions. Step 3.5D does not permanently delete events.
- Deadline urgency labels: Overdue, Today, This week, Upcoming, and Future.
- A summary endpoint for dashboard cards and next-event display.
- Safe audit events for admin create/update/cancel and command-driven event sync.
- Idempotent demo data and idempotent course-section deadline sync commands.
- A shared frontend `/calendar` route with summary cards, month/list views, filters, event details, role-specific My Deadlines, and admin create/edit/cancel controls.
- Documentation that prepares calendar data for later AI/RAG deadline answering without implementing AI.

## Non-Goals

Step 3.5D does not implement Step 3.5E Admin Reporting Dashboard, Step 3.5F Student Document Management, Step 3.5G Admissions, AI co-pilot, at-risk scoring, wellbeing workflows, recurring rules, personal reminders, email/SMS/push reminders, Google Calendar or Outlook sync, Moodle assignment deadline import, full scheduling/timetable conflict detection, or a new design system.

## Design Decisions

### Backend Model

Use a new `apps.calendar` Django app. `AcademicCalendarEvent` stores simple institutional dates:

- `id` UUID primary key
- `title`, `description`
- `event_type`: registration open, registration deadline, drop deadline, exam period, grade submission deadline, term start, term end, Moodle activity, advising, or general
- `audience`: all, students, faculty, advisors, or admins
- `priority`: low, normal, high, or critical
- `academic_year`, `semester`
- `start_at`, optional `end_at`, `all_day`
- optional `location`
- optional `related_course_section`
- `source`: manual, course section, system, or Moodle
- `status`: active, cancelled, or draft
- nullable `created_by`
- sanitized `metadata`
- timestamps

Validation rejects an `end_at` earlier than `start_at` and empty title/year/semester values. Metadata is sanitized before storage and serialization to avoid leaking tokens, credentials, raw JWTs, or private key material.

### API Behavior

Authenticated reads:

- `GET /api/v1/calendar/events/`
- `GET /api/v1/calendar/events/<id>/`
- `GET /api/v1/calendar/summary/`

Admin writes:

- `POST /api/v1/calendar/events/`
- `PATCH /api/v1/calendar/events/<id>/`
- `POST /api/v1/calendar/events/<id>/cancel/`

Visibility:

- Students see `ALL` and `STUDENTS` active events.
- Faculty see `ALL` and `FACULTY` active events.
- Advisors see `ALL` and `ADVISORS` active events.
- Admins see all audiences and all statuses unless filtered.

List filters support `month`, `start`, `end`, `event_type`, `audience`, `semester`, `academic_year`, and `status`.

The summary endpoint returns counts for upcoming events, registration deadlines, exam periods, grade deadlines, current academic year/semester, and the next visible event.

### Course Section Sync

`sync_academic_calendar_from_sections` creates or updates course-section source events for:

- registration opens
- registration deadline
- drop deadline

Idempotency uses `(source, related_course_section, event_type)`. This keeps the command safe to rerun and avoids duplicate deadline spam.

### Demo Seed

`seed_academic_calendar_demo` creates safe local events for term start, registration opens, registration deadline, drop/add deadline, advising week, exam period, grade submission deadline, and term end. The command does not require Moodle, stores no secrets, and uses stable metadata keys to avoid duplicates on rerun.

### Audit And Notifications

Calendar create, update, cancel, demo seed, and section sync actions record audit events. Use `ACADEMIC_CALENDAR` as a new audit category so Step 3.5C can filter calendar activity clearly.

Automatic notification fan-out is intentionally not enabled by default. If the admin form includes `Notify affected users`, only active `HIGH` or `CRITICAL` manually-created events may create in-app notifications for the targeted audience. The checkbox defaults unchecked.

### Frontend

Add `/calendar` for `STUDENT`, `ADVISOR`, `FACULTY`, and `ADMIN`. Add Academic Calendar sidebar links:

- Student section after Registration.
- Faculty teaching section.
- Advisor advising section.
- Admin Academic Operations after Courses.

The page uses existing Tailwind tokens, shared UI components, Heroicons, and the Step 3.5B/3.5C app shell polish.

Top-level sections:

- Summary cards: Upcoming Events, Registration Deadlines, Exam Periods, Grade Deadlines, Next Event.
- My Deadlines panel using the same event list, filtered by role-relevant event types and priority.
- Main Academic Calendar panel with month/list view modes, month navigation, and filters.
- Event details panel.
- Admin modal for create/edit/cancel with no delete action.
- Current Scope card documenting implemented and future boundaries.

Accessibility requirements:

- Buttons have visible text or aria labels.
- Event chips are keyboard-focusable.
- Selected event has visible focus state.
- Badges include text and color is never the only signal.
- Month grid has readable day labels.
- Forms have labels tied to inputs.
- Error messages are readable and specific.
- Modal close controls remain keyboard accessible.
- List view remains available as the accessible/mobile fallback.

Mobile behavior:

- Filters wrap cleanly.
- Month grid uses horizontal overflow if needed.
- List view is the safest narrow-screen mode.
- Event detail panel stacks below list/grid on smaller screens.

## Risks And Mitigations

- Course section dates already exist and can conflict with manual calendar events. The sync command uses `COURSE_SECTION` source and visible source labels so admins can distinguish generated dates from manual dates.
- Broad notification fan-out could spam users. Notifications stay opt-in and limited to high/critical events.
- Calendar grids are weaker for screen readers. List view is first-class and always available.
- Metadata can accidentally contain secrets. Calendar services sanitize metadata on write and serializers sanitize again on output.
- Enrollment-rule enforcement should eventually consult central calendar data, but Step 3.5D does not change enrollment/drop behavior to avoid regressions.

## Testing Requirements

Backend tests cover role-aware visibility, admin write permissions, validation, filters, summary counts, demo seed, section sync, audit hooks, and metadata secret safety.

Frontend tests cover route/sidebar registration, summary cards, month/list view rendering, filters, details panel, admin-only controls, create/cancel mutations, empty/error states, and absence of emoji page text where practical.
