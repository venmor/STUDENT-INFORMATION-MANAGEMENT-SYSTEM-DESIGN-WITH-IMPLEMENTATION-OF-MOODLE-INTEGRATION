# Software Requirements Specification (SRS)
## Modern Student Information System with Moodle Integration & AI Layer
### University of Zambia — Department of Computer Science
**Authors:** Chitundu Milimbo & Charles Hangoma  
**Supervisor:** Prof. J Phiri  
**Version:** 1.1 — Pre-Implementation Baseline Revision  
**Date:** April 2026  

---

## Revision History

| Version | Date | Summary |
|---|---|---|
| 1.0 | April 2026 | Initial draft for supervisor review |
| 1.1 | April 2026 | Locked implementation baseline, clarified role model, corrected integration references, tightened privacy and wellbeing requirements, and added phased delivery guidance |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall System Description](#2-overall-system-description)
3. [Functional Requirements](#3-functional-requirements)
   - 3.1 [Student Records Module](#31-student-records-module)
   - 3.2 [Course Catalog Module](#32-course-catalog-module)
   - 3.3 [Enrollment Management Module](#33-enrollment-management-module)
   - 3.4 [Grade Management Module](#34-grade-management-module)
   - 3.5 [User Administration & RBAC](#35-user-administration--rbac)
4. [Non-Functional Requirements](#4-non-functional-requirements)
   - 4.1 [Performance](#41-performance)
   - 4.2 [Security & Authentication](#42-security--authentication)
   - 4.3 [Data Protection & Privacy](#43-data-protection--privacy)
   - 4.4 [Availability & Reliability](#44-availability--reliability)
   - 4.5 [Usability](#45-usability)
   - 4.6 [Maintainability & Scalability](#46-maintainability--scalability)
   - 4.7 [Accessibility](#47-accessibility)
5. [Moodle Integration Requirements](#5-moodle-integration-requirements)
   - 5.1 [Lane A — Provisioning & Synchronisation](#51-lane-a--provisioning--synchronisation)
   - 5.2 [Lane B — LTI v1.3 Tool Embedding](#52-lane-b--lti-v13-tool-embedding)
   - 5.3 [Data Flow Diagrams](#53-data-flow-diagrams)
   - 5.4 [Error Handling & Retry Policy](#54-error-handling--retry-policy)
6. [AI Capability Requirements](#6-ai-capability-requirements)
   - 6.1 [Student Service Co-pilot](#61-student-service-co-pilot)
   - 6.2 [Staff Workflow Acceleration (Summarisation)](#62-staff-workflow-acceleration-summarisation)
   - 6.3 [At-Risk Student Insight Engine](#63-at-risk-student-insight-engine)
   - 6.4 [Opt-In Wellbeing Support](#64-opt-in-wellbeing-support)
   - 6.5 [AI Governance Requirements (All Features)](#65-ai-governance-requirements-all-features)
7. [System Constraints](#7-system-constraints)
8. [Assumptions & Dependencies](#8-assumptions--dependencies)
9. [Glossary](#9-glossary)
10. [Supervisor Sign-off](#10-supervisor-sign-off)

---

## 1. Introduction

### 1.1 Purpose of This Document

This Software Requirements Specification (SRS) defines the complete functional and non-functional requirements for the Modern Student Information System (SIS). It serves as the authoritative contract between the development team and the project supervisor. No implementation work on any module begins until the relevant section of this document has been reviewed and signed off.

### 1.2 Scope

The system being specified is a web-based academic management platform with three integrated components:

- A **core SIS** providing student records, course management, enrollment, grades, and user administration.
- A **Moodle integration layer** using two complementary lanes: the Moodle REST web services API (provisioning and synchronisation) and IMS Global LTI v1.3 (tool embedding).
- An **AI/LLM governance layer** providing a student service co-pilot, staff workflow summarisation, at-risk student detection, and opt-in wellbeing support — all governed under the NIST AI Risk Management Framework.

### 1.3 Intended Audience

| Audience | How they use this document |
|---|---|
| Development team | Implementation reference — every feature must trace to a requirement ID here |
| Project supervisor | Review and sign-off authority |
| Testers | Basis for all test cases — each requirement becomes at least one test |
| Future maintainers | Understanding design decisions and system boundaries |

### 1.4 Requirement ID Format

Every requirement in this document is assigned a unique ID using the format:

```
[MODULE]-[TYPE]-[NUMBER]
```

| Prefix | Meaning |
|---|---|
| `FR` | Functional Requirement |
| `NFR` | Non-Functional Requirement |
| `MI` | Moodle Integration Requirement |
| `AI` | AI Capability Requirement |

**Example:** `FR-STU-001` = Functional Requirement, Student Records module, number 001.

---

## 2. Overall System Description

### 2.1 System Context

The Modern SIS operates as the authoritative administrative record system for the institution. It does not replace Moodle — it governs it. The relationship between the two systems is:

- **SIS** = source of truth for all administrative and academic data (enrollment, grades, student records, financial flags)
- **Moodle** = dedicated learning environment (content delivery, assessment, discussion, collaboration)
- **Integration layer** = event-driven SIS → Moodle provisioning plus scheduled Moodle → SIS engagement ingestion, with LTI launches for embedded SIS tools
- **AI layer** = decision-support engine that synthesises data from both systems to help staff and students

### 2.2 User Roles

The system defines four primary roles. Every authenticated user is assigned exactly one primary role. Role determines which modules, data, and actions are accessible.

For exceptional access needs, the system also supports narrowly scoped capability flags. In v1, the only additional capability flag is `wellbeing_coordinator`. Capability flags do not replace the primary role model and do not grant broad administrative access.

| Role | Description | Primary concerns |
|---|---|---|
| **Student** | Enrolled learner | View own records, register for courses, access co-pilot, wellbeing check-in |
| **Advisor** | Academic advisor or personal tutor | Unified student profiles, at-risk alerts, advising notes, workflow summarisation |
| **Faculty** | Lecturer or instructor | Class rosters, grade entry, Moodle engagement view for own courses |
| **Admin** | Registrar or IT administrator | All user management, full data access, system configuration, AI audit log review |

### 2.3 System Boundaries

**In scope:**
- All modules listed in Section 3
- Moodle integration as defined in Section 5
- AI capabilities as defined in Section 6
- Web-based responsive interface (desktop and mobile browser)

**Out of scope:**
- Native mobile applications (iOS/Android)
- Financial aid processing or fee payment gateway integration beyond status flag display
- Modification of Moodle core code (all integration uses standard APIs only)
- Training LLM models from scratch (existing LLM APIs with prompt engineering and RAG only)
- Migration of historical data from any existing SIS (representative test dataset used for development)

### 2.4 Approved Implementation Baseline

The following implementation baseline is approved for v1.1. Any change to these choices after sign-off requires an ADR and supervisor approval.

| Layer | Approved baseline |
|---|---|
| Backend | Python 3.11+, Django 5, Django REST Framework |
| Frontend | React 18, TypeScript, Vite |
| Database | MySQL 8.0 |
| Async jobs / queue | Celery + Redis |
| Moodle integration | Moodle REST web services API + PyLTI1p3 |
| Vector store | Qdrant |
| AI provider model | OpenAI-compatible gateway, provider configurable per environment |
| Containerisation | Docker Compose for development and staging; Docker-based Linux deployment for production |
| CI/CD | GitHub Actions |

### 2.5 Phased Delivery Baseline

To reduce implementation and operational risk, delivery shall proceed in phases:

| Phase | Included scope |
|---|---|
| **Phase 1 (MVP)** | Core SIS modules, authentication, RBAC, audit logging, Moodle Lane A provisioning and reconciliation |
| **Phase 2** | Moodle Lane B embedded tools, AI student co-pilot, staff workflow summarisation |
| **Phase 3** | At-risk student insight engine |
| **Phase 4** | Opt-in wellbeing support, contingent on institutional policy and safeguarding approval |

---

## 3. Functional Requirements

### 3.1 Student Records Module

This module manages the authoritative academic and personal record for every student in the institution.

#### 3.1.1 Student Profile Management

| ID | Requirement | Priority |
|---|---|---|
| `FR-STU-001` | The system shall allow admins to create a new student record with the following mandatory fields: full name, national ID or student number, date of birth, gender, programme of study, year of study, and contact email. | Must Have |
| `FR-STU-002` | The system shall allow admins to read any student record in full. Advisors shall be able to read the full academic record of students assigned to them, excluding restricted wellbeing records. | Must Have |
| `FR-STU-003` | The system shall allow admins to update any field on a student record, with a change log capturing who edited what and when. | Must Have |
| `FR-STU-004` | The system shall allow admins to deactivate (soft-delete) a student record. Deactivated records are not deleted from the database but are excluded from active queries by default. | Must Have |
| `FR-STU-005` | The system shall allow students to view their own profile but not edit it directly. Any correction request is submitted as a flagged form routed to an admin for approval. | Must Have |
| `FR-STU-006` | The system shall display a student's Moodle engagement data (last login, assignment submission rate, quiz average) alongside their SIS profile data in the advisor view for the advisor's assigned students. | Must Have |
| `FR-STU-007` | The system shall maintain a full audit log of all reads and writes on student records, capturing timestamp, user ID, and action type. | Must Have |

#### 3.1.2 Academic Standing

| ID | Requirement | Priority |
|---|---|---|
| `FR-STU-008` | The system shall assign one of four academic standing statuses to each student: **Good Standing**, **Academic Warning**, **Probation**, **Suspended**. | Must Have |
| `FR-STU-009` | The system shall automatically recalculate academic standing after each grade entry cycle based on configurable GPA thresholds set by the admin. | Must Have |
| `FR-STU-010` | The system shall notify the student's assigned advisor via dashboard alert when a student's standing drops to Probation or Suspended. | Must Have |
| `FR-STU-011` | Admins shall be able to manually override academic standing with a mandatory reason field, which is recorded in the audit log. | Should Have |

#### 3.1.3 Attendance Tracking

| ID | Requirement | Priority |
|---|---|---|
| `FR-STU-012` | The system shall allow faculty to record attendance for each session of their assigned courses: Present, Absent, Excused. | Must Have |
| `FR-STU-013` | The system shall calculate an attendance percentage per student per course and display it in the student's unified profile. | Must Have |
| `FR-STU-014` | The system shall generate an attendance flag on a student's profile when their attendance in any course drops below a configurable threshold (default: 75%). | Must Have |
| `FR-STU-015` | Attendance flags shall be visible to the student's advisor on the unified profile dashboard and shall feed into the at-risk engine. | Must Have |

#### 3.1.4 Financial Flags & Advising Record

| ID | Requirement | Priority |
|---|---|---|
| `FR-STU-016` | The system shall allow admins to create, update, and clear financial status flags on a student record, capturing flag type, reason, effective date, and actor user ID. | Must Have |
| `FR-STU-017` | Active financial status flags shall be visible to the student, the student's assigned advisor, and admins. They shall not be visible to faculty by default. | Must Have |
| `FR-STU-018` | Financial status flags shall be read-only indicators in v1. They may inform enrollment and advising decisions, but v1 shall not process payments or automatically clear holds from external payment events. | Must Have |
| `FR-STU-019` | Advisors and admins shall be able to create advising notes linked to a student record. | Must Have |
| `FR-STU-020` | Advising notes shall support `Draft` and `Approved` states. Only the approved version becomes part of the official advising record. | Must Have |
| `FR-STU-021` | All create, update, approval, and read events for advising notes shall be audit logged with timestamp, actor user ID, and action type. | Must Have |

---

### 3.2 Course Catalog Module

This module manages the institution's official course offerings and timetable.

| ID | Requirement | Priority |
|---|---|---|
| `FR-CRS-001` | The system shall allow admins to create a course with: course code, course title, department, credit hours, description, prerequisites, and maximum enrollment capacity. | Must Have |
| `FR-CRS-002` | The system shall allow admins to create one or more sections per course, each with: section code, assigned faculty, room, timetable (day, start time, end time), and semester/academic year. | Must Have |
| `FR-CRS-003` | The system shall allow admins and faculty to read the full course catalog. Students shall see the catalog filtered to courses relevant to their programme. | Must Have |
| `FR-CRS-004` | The system shall allow admins to update any course or section detail. All changes are logged with user ID and timestamp. | Must Have |
| `FR-CRS-005` | The system shall allow admins to archive a course section at the end of a semester without deleting historical enrollment and grade data. | Must Have |
| `FR-CRS-006` | The system shall enforce prerequisite checks at enrollment: if a student attempts to enroll in a course whose prerequisites they have not passed, the system shall block the enrollment and display a clear reason. | Must Have |
| `FR-CRS-007` | The system shall enforce capacity limits: if a section is full, the student shall be offered a waitlist option. | Must Have |

---

### 3.3 Enrollment Management Module

This module manages the process of linking students to course sections for a given semester.

| ID | Requirement | Priority |
|---|---|---|
| `FR-ENR-001` | The system shall allow students to self-enroll in open course sections during the designated registration window, subject to prerequisite and capacity checks. | Must Have |
| `FR-ENR-002` | The system shall allow students to drop a course during the designated drop window. After the drop deadline, only an admin can process a late drop with a mandatory reason field. | Must Have |
| `FR-ENR-003` | The system shall allow advisors to enroll or drop a student in any course on their behalf, with the action logged against the advisor's user ID. | Must Have |
| `FR-ENR-004` | The system shall allow admins to perform bulk enrollment via CSV file upload. The system shall validate each row, display a preview with flagged errors before committing, and generate an import report. | Must Have |
| `FR-ENR-005` | The system shall automatically trigger Moodle enrollment synchronisation (`MI-A-010` / `MI-A-011`) within 10 seconds of any enrollment or drop event. | Must Have |
| `FR-ENR-006` | The system shall maintain a complete enrollment history per student, including all add, drop, and transfer events with timestamps and actor user IDs. | Must Have |
| `FR-ENR-007` | The system shall display current enrollment count and remaining capacity on each section in real time. | Should Have |
| `FR-ENR-008` | The system shall send an email or in-app notification to the student confirming successful enrollment or drop. | Should Have |
| `FR-ENR-009` | Where a section uses a waitlist, the system shall maintain the waitlist in chronological order of join time and allow admins to promote the next eligible student when capacity becomes available. | Should Have |

---

### 3.4 Grade Management Module

This module manages the entry, calculation, and official recording of student grades.

| ID | Requirement | Priority |
|---|---|---|
| `FR-GRD-001` | The system shall allow faculty to enter a grade for each enrolled student in their assigned course sections. Grades are entered as a numeric score (0–100) and automatically converted to a letter grade and grade point using a configurable grading scale. | Must Have |
| `FR-GRD-002` | The system shall maintain two grade states: **Draft** (visible only to the entering faculty and admins) and **Official** (released to the student and used in GPA calculation). Faculty submit grades as draft; only admins can mark them official. | Must Have |
| `FR-GRD-003` | The system shall calculate and update a student's cumulative GPA automatically whenever new official grades are committed. | Must Have |
| `FR-GRD-004` | The system shall generate a printable and downloadable transcript for any student on demand, showing all official grades and cumulative GPA. Transcripts must be generated as PDF. | Must Have |
| `FR-GRD-005` | The system shall allow admins to record a grade change after the official grade has been set, with a mandatory reason field and full audit log entry. | Must Have |
| `FR-GRD-006` | The system shall automatically trigger grade pass-back to Moodle (`MI-A-013`) within 30 seconds of a grade being marked official. | Must Have |
| `FR-GRD-007` | The system shall display each student's grade history (all semesters) on the advisor's unified profile view. | Must Have |
| `FR-GRD-008` | The system shall support incomplete grade codes (I) and withdrawal codes (W) in addition to standard letter grades. | Should Have |

---

### 3.5 User Administration & RBAC

This module manages all system user accounts and enforces role-based access control across every module.

| ID | Requirement | Priority |
|---|---|---|
| `FR-USR-001` | The system shall allow admins to create user accounts with: full name, email address, assigned primary role (student, advisor, faculty, admin), and a temporary initial password that must be changed on first login. | Must Have |
| `FR-USR-002` | The system shall enforce role-based access control on every API endpoint and every UI route. A user without the required role shall receive a 403 Forbidden response, not a redirect to login. | Must Have |
| `FR-USR-003` | The system shall allow admins to deactivate any user account. Deactivated accounts cannot log in; all historical data associated with the account is preserved. | Must Have |
| `FR-USR-004` | The system shall allow admins to assign a student to a specific advisor. A student can only be assigned to one advisor at a time. | Must Have |
| `FR-USR-005` | The system shall allow admins to assign faculty to specific course sections. Faculty can only enter grades and view rosters for sections assigned to them. | Must Have |
| `FR-USR-006` | The system shall allow any user to change their own password after verifying their current password. Admins can force a password reset without knowing the current password. | Must Have |
| `FR-USR-007` | The system shall enforce password policy: minimum 10 characters, at least one uppercase letter, one lowercase letter, one digit, and one special character. | Must Have |
| `FR-USR-008` | The system shall allow admins to view a full access log for any user account: all logins, failed login attempts, and API actions. | Must Have |
| `FR-USR-009` | The system shall allow admins to assign or revoke the `wellbeing_coordinator` capability flag for designated staff. This capability grants access only to wellbeing-specific views and workflows. | Must Have |

#### RBAC Permission Matrix

| Action | Student | Advisor | Faculty | Admin |
|---|:---:|:---:|:---:|:---:|
| View own profile | ✅ | — | — | ✅ |
| View assigned advisee profile | — | ✅ | — | ✅ |
| Edit student profile | — | — | — | ✅ |
| View course catalog | ✅ | ✅ | ✅ | ✅ |
| Create / edit courses | — | — | — | ✅ |
| Self-enroll in course | ✅ | — | — | — |
| Enroll student in course | — | ✅ | — | ✅ |
| View own grades | ✅ | — | — | ✅ |
| Enter grades (own sections) | — | — | ✅ | ✅ |
| Mark grades official | — | — | — | ✅ |
| Mark attendance | — | — | ✅ | ✅ |
| View at-risk alerts | — | ✅ | — | ✅ |
| Use AI co-pilot | ✅ | — | — | — |
| Use AI summarisation | — | ✅ | — | ✅ |
| View AI audit log | — | — | — | ✅ |
| Create / deactivate users | — | — | — | ✅ |
| View wellbeing check-in data | — | — | — | ✅* |

`*` Requires the `wellbeing_coordinator` capability flag in addition to the user's primary role.

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement | Target |
|---|---|---|
| `NFR-PER-001` | **API response time** — 95% of all API requests shall complete within 2 seconds under normal load (up to 200 concurrent users). | < 2s at p95 |
| `NFR-PER-002` | **Page load time** — Initial page load (first contentful paint) for all major dashboard views shall complete within 3 seconds on a standard university network connection. | < 3s FCP |
| `NFR-PER-003` | **Moodle sync latency** — User and enrollment provisioning to Moodle shall complete within 10 seconds of the triggering SIS event. | < 10s |
| `NFR-PER-004` | **Grade pass-back latency** — Official grades shall be reflected in the Moodle gradebook within 30 seconds of being marked official in the SIS. | < 30s |
| `NFR-PER-005` | **AI co-pilot response time** — The student service co-pilot shall return a response within 8 seconds for 95% of queries. | < 8s at p95 |
| `NFR-PER-006` | **At-risk engine runtime** — The nightly at-risk processing job shall complete for a cohort of up to 5,000 active students within 60 minutes. | < 60 min |
| `NFR-PER-007` | **Transcript generation** — PDF transcript generation shall complete within 5 seconds for any student record. | < 5s |
| `NFR-PER-008` | **Bulk enrollment import** — A CSV import of up to 500 rows shall complete within 30 seconds. | < 30s for 500 rows |

---

### 4.2 Security & Authentication

| ID | Requirement | Detail |
|---|---|---|
| `NFR-SEC-001` | **JWT authentication** — All API requests shall require a valid JWT Bearer token in the Authorization header, except explicitly public endpoints: `/auth/login`, `/auth/refresh`, `GET /lti/login`, `POST /lti/launch`, and `GET /lti/jwks`. | Access token expiry: 15 minutes. Refresh token expiry: 7 days. |
| `NFR-SEC-002` | **HTTPS only** — All HTTP traffic shall be automatically redirected to HTTPS. No sensitive data shall ever be transmitted over an unencrypted connection. | TLS 1.2 minimum; TLS 1.3 preferred. |
| `NFR-SEC-003` | **Password hashing** — All passwords shall be hashed using bcrypt with a minimum work factor of 12 before storage. Plain-text passwords shall never be stored or logged. | bcrypt, cost factor ≥ 12. |
| `NFR-SEC-004` | **LTI JWT validation** — All LTI v1.3 launch requests shall be validated by verifying the JWT signature against the Moodle-published JWKS, checking the `iss`, `aud`, `exp`, and `nonce` claims. Expired or replayed tokens shall be rejected with HTTP 401. | PyLTI1p3 library. |
| `NFR-SEC-005` | **Role enforcement** — Every API endpoint and every frontend route shall enforce role-based access control. Endpoints shall return HTTP 403 (not 404) for authorised but unpermitted requests to avoid enumeration. | Middleware-level, not handler-level. |
| `NFR-SEC-006` | **SQL injection prevention** — All database queries shall use parameterised queries or an ORM. No raw string interpolation of user input into SQL. | Enforced by Django ORM except for explicitly reviewed reporting queries. |
| `NFR-SEC-007` | **XSS prevention** — All user-supplied content rendered in the browser shall be escaped by the frontend framework. The Content-Security-Policy header shall be set on all responses. | React auto-escaping + CSP header. |
| `NFR-SEC-008` | **Rate limiting** — Login endpoints shall be rate-limited to 10 attempts per IP per minute. AI endpoints shall be rate-limited to 60 requests per user per hour. | Redis-backed rate limiter. |
| `NFR-SEC-009` | **Secrets management** — All credentials (database passwords, LLM API keys, Moodle tokens, LTI private keys) shall be stored in environment variables or a secrets manager. They shall never appear in source code or version control. | `.env` files gitignored; CI secrets via GitHub Actions secrets. |
| `NFR-SEC-010` | **OWASP Top 10** — The system shall be tested against all current OWASP Top 10 vulnerabilities before deployment using automated scanning (OWASP ZAP) and manual penetration testing of authentication and authorisation flows. | Pre-deployment gate. |

---

### 4.3 Data Protection & Privacy

| ID | Requirement | Detail |
|---|---|---|
| `NFR-PRI-001` | **Data minimisation** — The system shall collect only the data fields explicitly required by the functional requirements. No additional personal data shall be collected without documented justification. | Institutional privacy-by-design principle. |
| `NFR-PRI-002` | **Purpose limitation** — Student data collected for administrative purposes shall not be used for any other purpose without explicit student consent. AI training is not permitted on student personal data. | Institutional privacy policy and applicable law. |
| `NFR-PRI-003` | **Student data access** — Students shall be able to view all personal data held about them in the system via their profile page or account settings, subject to safeguarding restrictions on third-party notes. | Student right-of-access principle. |
| `NFR-PRI-004` | **Wellbeing data isolation** — Wellbeing check-in data shall be stored in a separate database schema accessible only to users with the designated `wellbeing_coordinator` capability. It shall be excluded from all general analytics queries and administrative views. | Strict access control. |
| `NFR-PRI-005` | **Wellbeing data deletion** — Students shall be able to permanently delete their entire wellbeing check-in history at any time via a one-click option in their account settings. Deletion shall remove the original mood values and free-text content within 24 hours. Restricted compliance logs may retain minimal metadata only (event ID, triage class, deletion event, timestamp, actor) and shall not retain deleted free-text content. | Consent-based. |
| `NFR-PRI-006` | **AI input/output logging** — All inputs to and outputs from the LLM layer shall be logged to the `ai_audit_log` table. Logs shall be retained for a minimum of 2 years. Logs shall not be used for LLM training without explicit institutional authorisation. Wellbeing free-text shall not be copied into `ai_audit_log`; it shall remain confined to restricted wellbeing storage. | Audit requirement. |
| `NFR-PRI-007` | **Database encryption at rest** — All database volumes shall be encrypted at rest using AES-256 or equivalent. | Infrastructure-level. |
| `NFR-PRI-008` | **Data export** — Admins shall be able to export a complete data export for any student in JSON format within 72 hours of an approved formal data access request. | Service target under institutional process. |
| `NFR-PRI-009` | **Legal and safeguarding review gate** — Before production use, the institution shall approve the privacy notice, retention schedule, consent language, and safeguarding process for wellbeing-related data. | Pre-deployment governance gate. |

---

### 4.4 Availability & Reliability

| ID | Requirement | Target |
|---|---|---|
| `NFR-AVL-001` | **Uptime** — The system shall target 99% uptime during the academic semester (excluding scheduled maintenance windows communicated at least 48 hours in advance). | 99% uptime in-semester |
| `NFR-AVL-002` | **Moodle sync resilience** — If a Moodle web services call fails, the system shall queue the failed operation for retry using an exponential backoff strategy (1s, 2s, 4s, 8s, max 3 retries). After 3 failed retries, an alert shall be sent to the admin dashboard. | Celery retry queue. |
| `NFR-AVL-003` | **AI service fallback** — If the LLM API is unavailable, the co-pilot shall return a graceful degradation message directing the student to the Registrar's office. Other AI features shall display a service unavailable notice rather than failing silently. | Graceful degradation. |
| `NFR-AVL-004` | **Database backup** — The MySQL database shall be backed up daily to an off-site location. Backups shall be retained for 30 days. A backup restore test shall be performed monthly. | Daily backup. |
| `NFR-AVL-005` | **Zero-downtime deployment** — Production deployments shall use a rolling or blue-green update strategy that does not interrupt active user sessions. | Docker-based deployment strategy. |

---

### 4.5 Usability

| ID | Requirement |
|---|---|
| `NFR-USE-001` | The system shall be usable on any modern browser (Chrome 110+, Firefox 110+, Safari 16+, Edge 110+) without requiring plugins or extensions. |
| `NFR-USE-002` | All interfaces shall be responsive and usable on screens as small as 375px wide (smartphone portrait mode). |
| `NFR-USE-003` | Every form field shall display inline validation errors within 300ms of the user leaving the field, before form submission. |
| `NFR-USE-004` | All error messages shall be written in plain language that tells the user what went wrong and what action to take. Technical error codes shall not be exposed to end users. |
| `NFR-USE-005` | The system shall achieve a System Usability Scale (SUS) score of at least 70 during user acceptance testing. |
| `NFR-USE-006` | The AI co-pilot interface shall display a clear disclaimer that responses are AI-generated and should be verified with the Registrar for official matters. |

---

### 4.6 Maintainability & Scalability

| ID | Requirement |
|---|---|
| `NFR-MNT-001` | The backend shall be structured as independent, loosely coupled modules. Adding a new SIS module shall not require changes to existing modules. |
| `NFR-MNT-002` | All database schema changes shall be managed through versioned Django migrations. No manual SQL changes shall be applied to the production database. |
| `NFR-MNT-003` | All API endpoints shall be documented in an OpenAPI 3.1 specification maintained alongside the source code and kept in sync with the implementation. |
| `NFR-MNT-004` | The codebase shall maintain a minimum of 80% unit test coverage across all backend modules, measured on every CI build. |
| `NFR-MNT-005` | The system shall be containerised with Docker and deployable on any Linux server with Docker Engine installed, without manual environment configuration beyond providing a `.env` file. |
| `NFR-MNT-006` | The AI prompt templates for all four AI features shall be stored in configuration files (not hardcoded), allowing tuning without code changes or redeployment. |
| `NFR-MNT-007` | Significant architectural decisions (stack changes, integration strategy changes, data-retention changes) shall be recorded as Architecture Decision Records (ADRs) in the repository. |

---

### 4.7 Accessibility

| ID | Requirement |
|---|---|
| `NFR-ACC-001` | All core user journeys shall conform to WCAG 2.2 AA for keyboard access, colour contrast, visible focus states, and semantic labelling. |
| `NFR-ACC-002` | All interactive controls shall be fully operable by keyboard without requiring a mouse or touch-only interaction. |
| `NFR-ACC-003` | Form validation and error messages shall be programmatically associated with the relevant fields and announced to assistive technologies. |

---

## 5. Moodle Integration Requirements

### 5.1 Lane A — Provisioning & Synchronisation

Lane A uses the Moodle REST web services API with token-based authentication. The SIS acts as the master — it initiates all provisioning. Moodle is the target that mirrors the SIS state.

#### 5.1.1 Authentication & Connection

| ID | Requirement |
|---|---|
| `MI-A-001` | The SIS shall connect to Moodle's REST API using a dedicated service account token stored in an environment variable. The token shall never be committed to version control. |
| `MI-A-002` | All Moodle API calls shall use HTTPS. If the Moodle instance returns an SSL error, the sync operation shall fail, log the error, and alert the admin rather than falling back to HTTP. |

#### 5.1.2 User Provisioning

| ID | Moodle Web Service Function | Data Flow | Trigger |
|---|---|---|---|
| `MI-A-003` | `core_user_create_users` | SIS → Moodle: username, email, first name, last name, generated temporary password or external auth identifier, institution name | On new SIS user account creation |
| `MI-A-004` | `core_user_update_users` | SIS → Moodle: updated name or email | On SIS profile update (name/email fields only) |
| `MI-A-005` | `core_user_get_users` | Moodle → SIS: Moodle user ID | On first successful create (to store `moodle_user_id` in `moodle_user_map`) |
| `MI-A-006` | `core_user_update_users` (suspended = true) | SIS → Moodle: suspend flag | On SIS account deactivation |

#### 5.1.3 Course Provisioning

| ID | Moodle Web Service Function | Data Flow | Trigger |
|---|---|---|---|
| `MI-A-007` | `core_course_create_courses` | SIS → Moodle: course short name, full name, category, summary, start date, end date | On new SIS course section creation for active semester |
| `MI-A-008` | `core_course_update_courses` | SIS → Moodle: updated name, dates | On SIS course section update |
| `MI-A-009` | `core_course_get_courses` | Moodle → SIS: Moodle course ID | On first successful create (to store `moodle_course_id` in `moodle_course_map`) |

#### 5.1.4 Enrollment Synchronisation

| ID | Moodle Web Service Function | Data Flow | Trigger |
|---|---|---|---|
| `MI-A-010` | `enrol_manual_enrol_users` | SIS → Moodle: Moodle user ID, Moodle course ID, role ID (student or editingteacher) | On SIS enrollment creation |
| `MI-A-011` | `enrol_manual_unenrol_users` | SIS → Moodle: Moodle user ID, Moodle course ID | On SIS enrollment drop |
| `MI-A-012` | `core_enrol_get_enrolled_users` | Moodle → SIS: enrolled user list | Periodic reconciliation check (nightly) to detect drift |

#### 5.1.5 Grade Pass-Back

| ID | Moodle Web Service Function | Data Flow | Trigger |
|---|---|---|---|
| `MI-A-013` | `core_grades_update_grades` | SIS → Moodle: Moodle course ID, Moodle user ID, grade value (0–100) | On SIS grade marked official (`FR-GRD-006`) |
| `MI-A-014` | `gradereport_user_get_grade_items` | Moodle → SIS: grade item structure | On initial course setup (to obtain grade item IDs before writing grades) |

#### 5.1.6 Engagement Data Pull (for AI Layer)

| ID | Moodle Web Service Function | Data Flow | Trigger |
|---|---|---|---|
| `MI-A-015` | `core_user_get_users` + last access timestamp | Moodle → SIS data warehouse: last login date per student per course | Nightly ETL job (feeds at-risk engine) |
| `MI-A-016` | `mod_assign_get_submissions` | Moodle → SIS data warehouse: submission status per student per assignment | Nightly ETL job |
| `MI-A-017` | `mod_quiz_get_user_attempts` | Moodle → SIS data warehouse: quiz attempt scores per student | Nightly ETL job |
| `MI-A-018` | `mod_forum_get_forum_discussions_paginated` | Moodle → SIS data warehouse: forum post count per student per course | Nightly ETL job |

---

### 5.2 Lane B — LTI v1.3 Tool Embedding

Lane B uses the IMS Global LTI v1.3 standard. The SIS acts as the **LTI Tool Provider**. Moodle acts as the **LTI Platform**.

#### 5.2.1 LTI Security Infrastructure

| ID | Requirement |
|---|---|
| `MI-B-001` | The SIS shall generate a 2048-bit RSA key pair for LTI signing. The private key shall be stored in an environment variable. The public key shall be exposed at a JWKS endpoint. |
| `MI-B-002` | The SIS shall expose a JWKS endpoint at `GET /lti/jwks` returning the public key in JSON Web Key Set format. This endpoint shall be publicly accessible without authentication. |
| `MI-B-003` | The SIS shall expose an OIDC login initiation endpoint at `GET /lti/login`. Moodle redirects to this endpoint to begin every LTI launch. |
| `MI-B-004` | The SIS shall expose an LTI launch endpoint at `POST /lti/launch`. This endpoint shall: verify the JWT signature against Moodle's JWKS, validate `iss`, `aud`, `exp`, and `nonce` claims, extract user context (user ID, course context, role), create or resume an authenticated session, and redirect to the appropriate embedded tool. |
| `MI-B-005` | The nonce used in each LTI launch shall be stored in Redis with a 10-minute TTL. Replayed nonces shall be rejected with HTTP 401. |

#### 5.2.2 Embedded Tools

**Tool 1 — Advising Dashboard**

| ID | Requirement |
|---|---|
| `MI-B-006` | The SIS shall expose an advising dashboard tool at `/lti/tools/advising-dashboard` that is launchable from within any Moodle course page by users with the advisor or admin role. |
| `MI-B-007` | When launched, the advising dashboard shall display the Moodle course context, course roster, and engagement summary for that course. The advisor may select an enrolled student to open the unified student profile combining SIS data and Moodle engagement data for that student and course. If the launch includes an institution-defined student identifier custom parameter, that student may be preselected. |
| `MI-B-008` | The advising dashboard tool shall be read-only — no SIS data can be modified from within the embedded view. All edits must occur in the main SIS interface. |

**Tool 2 — Student Registration**

| ID | Requirement |
|---|---|
| `MI-B-009` | The SIS shall expose a student registration tool at `/lti/tools/registration` that is launchable from within Moodle by users with the student role. |
| `MI-B-010` | When launched, the registration tool shall display the student's current enrollments, available courses for the current semester, and a Register / Drop action for each eligible section. |
| `MI-B-011` | Any enrollment or drop action taken within the embedded registration tool shall be processed by the standard SIS enrollment engine and shall trigger the same Moodle provisioning sync as a direct SIS action (`FR-ENR-005`). |

---

### 5.3 Data Flow Diagrams

#### Lane A — Provisioning Flow (text representation)

```
SIS Event (new student created)
        │
        ▼
SIS Sync Engine (Celery task)
        │
        ├─── core_user_create_users ──────► Moodle
        │                                       │
        │◄──── Moodle user ID ──────────────────┘
        │
        ▼
moodle_user_map table
(sis_user_id → moodle_user_id stored)
```

#### Lane B — LTI v1.3 Launch Flow (text representation)

```
User clicks LTI tool link in Moodle
        │
        ▼
Moodle redirects to: GET /lti/login
        │  (client_id, login_hint, target_link_uri)
        ▼
SIS validates params, generates nonce, stores in Redis
        │
        ▼
SIS redirects back to Moodle OIDC endpoint
        │
        ▼
Moodle generates signed JWT, POSTs to: POST /lti/launch
        │
        ▼
SIS validates JWT (signature + claims + nonce)
        │
        ▼
SIS extracts user context, creates session
        │
        ▼
SIS redirects user to embedded tool URL
(/lti/tools/advising-dashboard or /lti/tools/registration)
```

---

### 5.4 Error Handling & Retry Policy

| Scenario | Behaviour |
|---|---|
| Moodle API call returns HTTP 5xx | Log error, queue Celery retry with exponential backoff (1s → 2s → 4s). After 3 failures, create admin alert. |
| Moodle API call returns HTTP 401 (token expired) | Log error, send admin alert to rotate the Moodle API token. Do not retry automatically. |
| LTI JWT validation fails (bad signature) | Return HTTP 401. Log the attempt with requesting IP. Do not create a session. |
| LTI JWT expired (`exp` claim in the past) | Return HTTP 401. Log the attempt. |
| LTI nonce replay detected | Return HTTP 401. Log the attempt. Flag for security review if frequency exceeds 5 per minute from same IP. |
| Moodle course not found for grade pass-back | Log the error, create an admin alert, and flag the grade record as `sync_failed` in the SIS for manual resolution. |
| Nightly ETL job fails mid-run | Log the failure point, send admin alert. The at-risk engine shall not run until the ETL job completes successfully to avoid processing stale data. |

---

## 6. AI Capability Requirements

> **Governance principle applied to all AI features:**  
> The AI layer is a **decision-support engine**, not an autonomous decision maker. No AI output becomes an official institutional record without explicit human review and approval. Every AI interaction is logged. All features are governed under the NIST AI Risk Management Framework.

---

### 6.1 Student Service Co-pilot

#### 6.1.1 Purpose

To provide students with instant, accurate answers to routine administrative questions at any time of day, reducing queue load on the Registrar's office and improving student experience.

#### 6.1.2 Knowledge Sources

The co-pilot answers questions exclusively from the following institution-approved sources. It shall not answer from general LLM training knowledge on institutional matters.

| Source Document | Update Frequency | Ingestion Method |
|---|---|---|
| Course catalog (current academic year) | Each semester | PDF → text extraction → chunked embedding |
| Academic regulations and policies | On policy change | PDF → text extraction → chunked embedding |
| Academic calendar (registration, exam, fee deadlines) | Each semester | PDF/structured data → chunked embedding |
| Fee schedule | Each semester | PDF → text extraction → chunked embedding |
| Graduation requirements by programme | On change | PDF → text extraction → chunked embedding |
| Frequently asked questions (admin-curated) | Monthly | Structured Q&A pairs → direct embedding |

#### 6.1.3 Functional Requirements

| ID | Requirement |
|---|---|
| `AI-COP-001` | The co-pilot shall accept natural language queries from authenticated students via a chat interface in the student portal. |
| `AI-COP-002` | On each query, the system shall embed the question, retrieve the top-5 most relevant chunks from the vector store using cosine similarity, and construct a prompt that includes the retrieved context and the question. |
| `AI-COP-003` | The LLM shall be instructed to answer only from the provided context. If the context does not contain sufficient information to answer the question, the response shall state: *"I don't have enough information to answer this accurately. Please contact the Registrar's office or your academic advisor."* |
| `AI-COP-004` | Every response shall include source references showing which document and section the answer was drawn from, so the student can verify independently. |
| `AI-COP-005` | Every co-pilot interaction (query, retrieved chunks, response, timestamp, student ID, session ID) shall be written to `ai_audit_log` before the response is returned to the user. |
| `AI-COP-006` | The interface shall display a persistent disclaimer: *"Responses are generated by AI and may not reflect the most recent policy changes. For official matters, verify with the Registrar's office."* |
| `AI-COP-007` | If the LLM API is unavailable, the co-pilot shall return a graceful fallback message and shall not expose error details to the student. |

#### 6.1.4 Accuracy Testing Requirements

| ID | Requirement |
|---|---|
| `AI-COP-008` | Before deployment, a test set of at least 30 representative questions shall be compiled, covering all six knowledge source categories. |
| `AI-COP-009` | Each test question shall be evaluated for: correct answer (✅), partially correct (⚠️), incorrect (❌), and appropriate refusal (✅ when question is out of scope). |
| `AI-COP-010` | The co-pilot shall achieve a minimum accuracy rate of 85% (correct or appropriate refusal) on the test set before the feature is approved for deployment. |

---

### 6.2 Staff Workflow Acceleration (Summarisation)

#### 6.2.1 Purpose

To reduce the time advisors and admin staff spend writing structured records from unstructured notes, without removing human accountability from any official record.

#### 6.2.2 Workflow

```
1. Advisor pastes or types raw notes into the summarisation input box
2. System sends text to LLM with a structured extraction prompt
3. LLM returns a structured JSON summary: { key_issues, recommended_actions, urgency_level }
4. System displays the structured summary to the advisor for review and editing
5. Advisor edits the summary as needed
6. Advisor clicks "Approve & Save" — the human-edited version is saved as the official record
7. System logs: raw input, original AI output, final human-approved text, approving user ID, timestamp
```

> **Critical rule:** The raw AI output is **never** stored as an official record. Only the human-approved version is committed to the advising record.

#### 6.2.3 Functional Requirements

| ID | Requirement |
|---|---|
| `AI-SUM-001` | The summarisation feature shall be accessible only to users with the advisor or admin role. |
| `AI-SUM-002` | The system shall accept raw text input of up to 5,000 characters. Inputs exceeding this limit shall display a truncation warning before submission. |
| `AI-SUM-003` | The LLM prompt shall instruct the model to extract and return a structured summary in JSON with exactly three fields: `key_issues` (array of strings), `recommended_actions` (array of strings), `urgency_level` (one of: Routine, Follow-up Needed, Urgent). |
| `AI-SUM-004` | The UI shall render the structured summary in an editable form — not as raw JSON — so the advisor can modify each field before approving. |
| `AI-SUM-005` | The "Approve & Save" action shall require a single explicit button click. It shall not be triggered by navigation or form auto-save. |
| `AI-SUM-006` | The system shall log the following to `ai_audit_log`: raw input text, original AI output (pre-edit), final saved text, approving user ID, student ID (if applicable), and timestamp. |
| `AI-SUM-007` | The feature shall display the following notice above the input box: *"AI-generated summaries must be reviewed and approved before saving. The saved record will reflect your approved version, not the raw AI output."* |

---

### 6.3 At-Risk Student Insight Engine

#### 6.3.1 Purpose

To surface early warning signals about students who may be heading toward academic difficulty, enabling advisors to intervene proactively rather than reactively.

#### 6.3.2 Signal Definitions

The engine combines signals from two sources. The following table defines every signal, its source, its severity weight, and the threshold that marks it as active.

**SIS Signals**

| Signal Name | Source | Threshold for Active | Severity Weight |
|---|---|---|---|
| `attendance_flag` | SIS attendance records | Attendance < 75% in any active course | High |
| `academic_probation` | SIS academic standing | Standing = Probation or Suspended | High |
| `financial_hold` | SIS financial status flag | Any active financial hold on record | Medium |
| `grade_decline` | SIS grade history | GPA dropped by ≥ 0.5 points vs. previous semester | Medium |
| `incomplete_grade` | SIS grade records | 2 or more Incomplete (I) grades in current semester | Medium |

**Moodle Signals**

| Signal Name | Source | Threshold for Active | Severity Weight |
|---|---|---|---|
| `moodle_inactivity` | Moodle last login timestamp | No Moodle login in any enrolled course for ≥ 14 consecutive days | High |
| `assignment_miss_rate` | Moodle assignment submissions | ≥ 2 missed assignment deadlines in current semester | Medium |
| `quiz_failure_pattern` | Moodle quiz attempts | Average quiz score < 40% across all quizzes in current semester | Medium |
| `forum_disengagement` | Moodle forum participation | Zero forum posts in courses where participation is required, for ≥ 21 days | Low |

#### 6.3.3 Severity Classification

| Severity | Condition |
|---|---|
| 🔴 High | Any 1 High signal active, OR any 3+ signals active of any weight |
| 🟡 Medium | Any 2 Medium signals active, OR 1 Medium + 2 Low signals |
| 🟢 Low | Any 1 Low or 1 Medium signal active in isolation |

#### 6.3.4 Functional Requirements

| ID | Requirement |
|---|---|
| `AI-RSK-001` | The at-risk engine shall run as a nightly Celery scheduled task, processing all students with active enrollments in the current semester. |
| `AI-RSK-002` | For each student, the engine shall evaluate all 9 signals defined in Section 6.3.2 and determine severity using the classification in Section 6.3.3. |
| `AI-RSK-003` | For each student with a Medium or High severity classification, the engine shall generate a natural-language summary using the LLM. The prompt shall include the active signals and instruct the model to write 2–3 sentences explaining the concern in plain language suitable for an advisor. |
| `AI-RSK-004` | Each alert shall be stored in `at_risk_alerts` with: student ID, severity level, list of active signals, LLM-generated explanation, creation timestamp, and acknowledged status (default: false). |
| `AI-RSK-005` | High and Medium severity alerts shall appear in the advisor's dashboard alert queue, sorted by severity (High first) and then by date. |
| `AI-RSK-006` | Advisors shall be able to acknowledge each alert with a single click. Acknowledgement records the advisor's user ID and timestamp. Acknowledged alerts are moved to a historical view, not deleted. |
| `AI-RSK-007` | If a student's signals resolve (all signals become inactive), the system shall automatically close the open alert and log the closure with timestamp. The advisor shall be notified on their next login. |
| `AI-RSK-008` | The signal thresholds defined in Section 6.3.2 shall be stored in a configuration file, not hardcoded, to allow adjustment without code changes. |
| `AI-RSK-009` | All at-risk alert generation events shall be logged to `ai_audit_log` including: student ID, signals evaluated, LLM prompt used, LLM output, and final stored explanation. |

---

### 6.4 Opt-In Wellbeing Support

#### 6.4.1 Purpose

To provide students with a low-friction, private, and consent-driven pathway to signal emotional or personal difficulty, and to route appropriate support resources or staff escalation without causing harm through automation.

#### 6.4.2 Consent & Opt-In Flow

```
1. Student navigates to Account Settings → Wellbeing & Support
2. Student reads a plain-language consent statement explaining:
   - What data is collected (mood rating, optional free text)
   - Who can see individual responses (only staff assigned the `wellbeing_coordinator` capability)
   - How data is used (triage to resources or staff escalation)
   - How to delete data (available at any time)
3. Student clicks "Enable Wellbeing Check-in" to activate the feature
4. A "Wellbeing Check-in" button appears in the student portal (invisible to unenrolled students)
5. Student can disable and delete all data at any time via the same settings page
```

#### 6.4.3 Triage Classification

| Input Classification | Trigger Condition | System Response |
|---|---|---|
| **Normal** | Mood rating ≥ 3, no distress keywords in text | Display general self-care resources and encouraging message |
| **Concerning** | Mood rating 2, or moderate distress keywords detected | Display curated counselling and support resources, prompt to talk to advisor |
| **Escalate** | Mood rating 1, or keywords indicating immediate risk | Immediately notify designated wellbeing coordinator via dashboard alert and email. Display crisis support contact details to student. |

> **Critical rule:** The system shall **never** send the student an automated message claiming to diagnose their mental health. All triage output is limited to resource suggestions or staff notification. The wellbeing coordinator contacts the student directly.

#### 6.4.4 Functional Requirements

| ID | Requirement |
|---|---|
| `AI-WBE-001` | The wellbeing check-in UI shall be visible only to students who have completed the opt-in consent flow. No student shall see the feature without having actively enabled it. |
| `AI-WBE-002` | The check-in form shall collect: mood rating (1–5 numeric scale with labelled anchors: 1 = Very difficult, 5 = Doing well) and optional free-text comment (max 500 characters). |
| `AI-WBE-003` | The triage classification (Normal / Concerning / Escalate) shall be determined by a deterministic rules engine using the mood rating and an institution-approved keyword/rule set aligned to the classification criteria in Section 6.4.3. The LLM may assist only with drafting supportive wording for non-escalation outcomes and shall not be the sole escalation decision-maker. |
| `AI-WBE-004` | For Escalate classifications, a real-time notification shall be sent to all users assigned the `wellbeing_coordinator` capability via dashboard alert and email within 60 seconds of the check-in submission. |
| `AI-WBE-005` | For Escalate classifications, the student shall immediately see a screen displaying crisis support contacts (University Counselling Centre contact details) alongside a message that a support team member has been notified. |
| `AI-WBE-006` | Individual wellbeing check-in records shall be accessible only to users assigned the `wellbeing_coordinator` capability. They shall be excluded from all advisor, faculty, and general admin views. |
| `AI-WBE-007` | Aggregate anonymised reports (weekly mood distribution across the student body, no individual identifiable) shall be available to admin users for institutional planning purposes. |
| `AI-WBE-008` | All wellbeing triage events shall be logged to a separate restricted `wellbeing_audit_log` table. The log shall capture only the minimum metadata required for safeguarding and audit: event ID, student ID, triage class, notification status, actor/system identifier, and timestamps. Deleted free-text content shall not remain in the audit log after a valid deletion request. |
| `AI-WBE-009` | Students shall be able to view their own check-in history via their account settings. They shall be able to delete individual entries or their entire history at any time. Deletion shall be complete and irreversible within 24 hours. |

---

### 6.5 AI Governance Requirements (All Features)

These requirements apply to every AI-powered feature in the system.

| ID | Requirement | NIST AI RMF Mapping |
|---|---|---|
| `AI-GOV-001` | All LLM API calls shall be routed through a central AI gateway service. The gateway shall enforce rate limits, apply content filters, and log all traffic before forwarding to the LLM provider. | GOVERN 1.2 |
| `AI-GOV-002` | The system shall maintain an `ai_audit_log` table recording: log ID, feature name, user ID, student ID (where applicable), session ID, full input prompt, full LLM output, human-approved version (where applicable), approval timestamp, approving user ID, provider name, model name, model version, and creation timestamp. Wellbeing events use the separate `wellbeing_audit_log`. | MEASURE 2.5 |
| `AI-GOV-003` | Admins shall be able to view and search the `ai_audit_log` via the admin console. Logs shall be filterable by feature, date range, user, and student ID. | MANAGE 2.2 |
| `AI-GOV-004` | AI audit logs shall be immutable after creation. No update or delete operation shall be permitted on log records via the API. | GOVERN 1.1 |
| `AI-GOV-005` | Before each semester, a designated admin shall review a random sample of at least 50 AI co-pilot interactions and 20 at-risk alert explanations for accuracy, bias, and appropriateness. Results shall be documented. | MEASURE 2.9 |
| `AI-GOV-006` | The LLM provider, model name, and model version used for each feature shall be recorded in the audit log on each call, enabling future traceability if a model is found to produce biased outputs. | MAP 1.5 |
| `AI-GOV-007` | A human review queue shall be maintained for co-pilot interactions flagged as low-confidence. Low-confidence shall be defined by system heuristics such as missing source citations, retrieval score below a configured threshold, or explicit model refusal/uncertainty markers. Flagged interactions shall be reviewed within 5 business days. | MANAGE 2.4 |
| `AI-GOV-008` | The AI governance plan shall be reviewed and updated at the start of each academic semester by the system admin and project supervisor. | GOVERN 1.6 |

---

## 7. System Constraints

| Constraint | Description |
|---|---|
| **Moodle version** | The integration is designed for Moodle 4.1 LTS or later. Earlier versions may not support LTI v1.3 Advantage or all required web service functions. |
| **LLM provider dependency** | The system depends on an external LLM API (OpenAI or equivalent). Changes to the provider's API terms, pricing, or availability directly affect the AI layer. A fallback provider configuration shall be maintained. |
| **Browser-only** | The system is a web application. No native mobile app is in scope for this project. All interfaces must function in a standard browser. |
| **Single institution** | This system is designed as a single-tenant application for one institution. Multi-tenancy is explicitly out of scope. |
| **No Moodle core modification** | All Moodle integration must use the standard Moodle web services API and LTI interfaces. Modifying Moodle's core PHP code or database schema directly is prohibited. |
| **Representative dataset** | Development and testing shall use a representative synthetic dataset. Live student data migration from any existing system is not in scope. |

---

## 8. Assumptions & Dependencies

| # | Assumption / Dependency |
|---|---|
| 1 | The institution has an active Moodle 4.1+ instance accessible over HTTPS with web services enabled by a Moodle administrator. |
| 2 | The institution can provide a dedicated Moodle web services token with sufficient permissions for all API calls listed in Section 5.1. |
| 3 | At least one designated staff member is assigned the `wellbeing_coordinator` capability and is actively staffed to respond. The escalation feature in Section 6.4 has no value if no staff member is assigned to respond. |
| 4 | The institution provides access to official source documents (course catalog, academic regulations, fee schedule) in PDF or structured format for knowledge base ingestion. |
| 5 | An LLM API key (OpenAI or equivalent) is available to the development team for the duration of the project. Costs are covered within the project budget (LLM API allocation: ZMW 20,000). |
| 6 | The deployment environment is a Linux server with Docker Engine installed and outbound internet access to the LLM API provider. |
| 7 | A MySQL 8.0+ database server is available. |
| 8 | The supervisor (Prof. J Phiri) will review and sign off on this SRS within 5 business days of submission, allowing Phase 2 development to begin on schedule. |

---

## 9. Glossary

| Term | Definition |
|---|---|
| **SIS** | Student Information System — the administrative platform defined by this document |
| **LMS** | Learning Management System — in this project, Moodle |
| **LTI** | Learning Tools Interoperability — the IMS Global standard enabling tools to be embedded in an LMS with single sign-on |
| **JWKS** | JSON Web Key Set — a published endpoint containing the public key used to verify JWT signatures |
| **JWT** | JSON Web Token — a signed, self-contained token used for authentication and LTI launch security |
| **OIDC** | OpenID Connect — the identity layer used in the LTI v1.3 launch flow |
| **RAG** | Retrieval-Augmented Generation — the technique of retrieving relevant documents from a vector store before generating an LLM response |
| **RBAC** | Role-Based Access Control — access control model where permissions are granted per role, not per individual user |
| **ETL** | Extract, Transform, Load — the nightly job that pulls engagement data from Moodle into the SIS data warehouse |
| **NIST AI RMF** | National Institute of Standards and Technology Artificial Intelligence Risk Management Framework (AI 100-1, 2023) |
| **Celery** | A distributed task queue for Python, used for background sync jobs and the at-risk engine |
| **GPA** | Grade Point Average — the weighted average of a student's grade points per credit hour |
| **Soft-delete** | A deletion pattern where records are marked inactive rather than physically removed from the database |
| **p95** | The 95th percentile — the value below which 95% of observations fall; used for response time benchmarks |

---

## 10. Supervisor Sign-off

This section is to be completed by the project supervisor after reviewing all sections of this document. Development on any phase shall not begin until the corresponding modules in this SRS have been signed off.

---

**SRS Version reviewed:** 1.0  
**Date of review:** ___________________________

---

| Module | Approved | Comments |
|---|---|---|
| Section 3 — Functional Requirements | ☐ Approved &nbsp;&nbsp; ☐ Revisions required | |
| Section 4 — Non-Functional Requirements | ☐ Approved &nbsp;&nbsp; ☐ Revisions required | |
| Section 5 — Moodle Integration Requirements | ☐ Approved &nbsp;&nbsp; ☐ Revisions required | |
| Section 6 — AI Capability Requirements | ☐ Approved &nbsp;&nbsp; ☐ Revisions required | |
| Section 7–8 — Constraints & Assumptions | ☐ Approved &nbsp;&nbsp; ☐ Revisions required | |

---

**Supervisor signature:** ___________________________  
**Print name:** Prof. J Phiri  
**Date:** ___________________________

---

**Student 1 signature:** ___________________________  
**Print name:** Chitundu Milimbo  
**Date:** ___________________________

---

**Student 2 signature:** ___________________________  
**Print name:** Charles Hangoma  
**Date:** ___________________________

---

> *This document is version-controlled in the project Git repository. Any change after supervisor sign-off must be recorded as a new version with a change log entry and re-submitted for supervisor review.*
