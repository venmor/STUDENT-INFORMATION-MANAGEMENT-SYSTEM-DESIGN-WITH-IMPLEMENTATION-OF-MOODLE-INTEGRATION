# Modern SIS Architecture Diagrams

This document collects the main architecture and workflow diagrams for the Modern SIS baseline. All diagrams use Mermaid syntax so they can be rendered directly by Markdown tooling that supports Mermaid.

These diagrams complement, but do not replace, the detailed requirements in [SRS_Modern_SIS.md](../project/SRS_Modern_SIS.md), the stack baseline in [ADR-001](ADR-001-technology-baseline.md), the stack rationale in [technology-stack.md](technology-stack.md), and the data model in [modern-sis-erd.md](../diagrams/modern-sis-erd.md).

Rendered exports based on this source are organized under [../diagrams/rendered/](../diagrams/rendered/).

## Diagram Index

1. Use Case Overview
2. System Context
3. Integration Lanes Overview
4. Container Architecture
5. Backend Component Diagram
6. Data Sensitivity Boundaries
7. Sequence: Enrollment And Moodle Sync
8. Sequence: LTI Launch
9. Sequence: Nightly ETL And At-Risk Processing
10. Sequence: Wellbeing Check-In
11. Activity: Student Enrollment
12. Activity: Wellbeing Triage
13. State: Grade Record Lifecycle
14. State: Enrollment Lifecycle
15. Deployment Diagram

## 1. Use Case Overview

```mermaid
flowchart LR
    Student[Student]
    Advisor[Advisor]
    Faculty[Faculty]
    Admin[Admin]
    Coordinator[Staff with wellbeing_coordinator]

    subgraph SIS["Modern SIS"]
        UC1([View own profile and transcript])
        UC2([Register or drop courses])
        UC3([Ask the student co-pilot])
        UC4([Review assigned student profile])
        UC5([Acknowledge at-risk alerts])
        UC6([Enter attendance and grades])
        UC7([Manage users, courses, and settings])
        UC8([Review audit logs and sync status])
        UC9([Review wellbeing escalations])
        UC10([Launch SIS tools from Moodle])
    end

    Student --> UC1
    Student --> UC2
    Student --> UC3
    Student --> UC10

    Advisor --> UC4
    Advisor --> UC5
    Advisor --> UC10

    Faculty --> UC6
    Faculty --> UC10

    Admin --> UC7
    Admin --> UC8
    Admin --> UC10

    Coordinator --> UC9
```

## 2. System Context

```mermaid
flowchart LR
    subgraph Users["Institutional Users"]
        Student[Student]
        Advisor[Advisor]
        Faculty[Faculty]
        Admin[Admin]
    end

    subgraph Platform["Modern SIS Platform"]
        Web[React Web Application]
        API[Django API and Services]
    end

    subgraph Data["Data and Storage"]
        MySQL[(MySQL)]
        Redis[(Redis)]
        Qdrant[(Qdrant)]
        Storage[(S3-compatible Object Storage)]
    end

    subgraph External["External Systems"]
        Moodle[Moodle LMS]
        AIGateway[OpenAI-compatible AI Gateway]
        Notify[Email and Notification Services]
    end

    Student --> Web
    Advisor --> Web
    Faculty --> Web
    Admin --> Web

    Web --> API
    API --> MySQL
    API --> Redis
    API --> Qdrant
    API --> Storage
    API --> Moodle
    API --> AIGateway
    API --> Notify
```

## 3. Integration Lanes Overview

```mermaid
flowchart LR
    SISData[SIS Operational Data]
    Moodle[Moodle LMS]
    EmbeddedTools[Embedded SIS Tools]
    Analytics[Analytics and AI Inputs]
    AI[AI Features]

    SISData --> LaneA["Lane A<br/>Provisioning and Grade Pass-Back"]
    LaneA --> Moodle

    Moodle --> LaneB["Lane B<br/>LTI v1.3 Launches"]
    LaneB --> EmbeddedTools

    SISData --> ETL["Scheduled Analytics Projection"]
    Moodle --> ETL
    ETL --> Analytics
    Analytics --> AI
```

## 4. Container Architecture

```mermaid
flowchart TB
    Browser[User Browser]

    subgraph AppHost["Linux Host / Docker Compose"]
        Proxy[Reverse Proxy<br/>Caddy or Nginx]
        Frontend[React Frontend]
        API[Django API]
        Worker[Celery Worker]
        Beat[Celery Beat]
        Redis[(Redis)]
        MySQL[(MySQL 8.0)]
        Qdrant[(Qdrant)]
    end

    subgraph External["External Services"]
        Moodle[Moodle LMS]
        AIGateway[AI Gateway]
        Storage[S3-compatible Storage]
        Email[Email Service]
    end

    Browser --> Proxy
    Proxy --> Frontend
    Proxy --> API

    API --> MySQL
    API --> Redis
    API --> Qdrant
    API --> Moodle
    API --> AIGateway
    API --> Storage
    API --> Email

    Beat --> Worker
    Worker --> Redis
    Worker --> MySQL
    Worker --> Qdrant
    Worker --> Moodle
    Worker --> AIGateway
    Worker --> Email
```

## 5. Backend Component Diagram

```mermaid
flowchart LR
    subgraph Backend["Django Backend"]
        Controllers[REST and LTI Controllers]
        Auth[Authentication and RBAC]
        StudentSvc[Student and Advising Services]
        AcademicSvc[Course, Enrollment, Attendance, and Grade Services]
        MoodleSvc[Moodle Sync Service]
        LTISvc[LTI Launch Service]
        AISvc[AI Orchestration Service]
        Governance[Audit and Governance Service]
        WellbeingSvc[Restricted Wellbeing Service]
        Persistence[ORM Models and Repositories]
    end

    Controllers --> Auth
    Controllers --> StudentSvc
    Controllers --> AcademicSvc
    Controllers --> LTISvc
    Controllers --> AISvc
    Controllers --> WellbeingSvc

    StudentSvc --> Persistence
    AcademicSvc --> Persistence
    MoodleSvc --> Persistence
    LTISvc --> Persistence
    AISvc --> Persistence
    Governance --> Persistence
    WellbeingSvc --> Persistence

    AcademicSvc --> MoodleSvc
    LTISvc --> Auth
    AISvc --> Governance
    WellbeingSvc --> Governance
```

## 6. Data Sensitivity Boundaries

```mermaid
flowchart LR
    subgraph MainSchema["Main Operational Schema"]
        Users[Users and Roles]
        Students[Students and Advising]
        Academic[Courses, Enrollments, Grades, Attendance]
        AILog[AI Audit Log]
        Alerts[At-Risk Alerts]
    end

    subgraph RestrictedSchema["Restricted Wellbeing Schema"]
        Checkins[Wellbeing Check-Ins]
        WAudit[Wellbeing Audit Log]
    end

    subgraph AIStores["AI Data Stores"]
        Vector[(Qdrant)]
        Docs[(Object Storage)]
    end

    Students --> AILog
    Academic --> Alerts
    Docs --> Vector
    Checkins --> WAudit
```

## 7. Sequence: Enrollment And Moodle Sync

```mermaid
sequenceDiagram
    actor Student
    participant UI as React App
    participant API as Django API
    participant DB as MySQL
    participant Queue as Celery Queue
    participant Worker as Celery Worker
    participant Moodle as Moodle REST API

    Student->>UI: Submit course registration
    UI->>API: POST /api/v1/enrollments
    API->>DB: Validate registration window
    API->>DB: Validate prerequisites and capacity
    API->>DB: Create enrollment record
    API->>Queue: Enqueue Moodle sync task
    API-->>UI: 201 Created
    Queue->>Worker: Deliver sync task
    Worker->>Moodle: enrol_manual_enrol_users(...)
    Moodle-->>Worker: Success
    Worker->>DB: Mark sync successful
```

## 8. Sequence: LTI Launch

```mermaid
sequenceDiagram
    actor Advisor
    participant Moodle as Moodle LMS
    participant LTI as Django LTI Service
    participant Redis as Redis
    participant DB as MySQL

    Advisor->>Moodle: Click advising dashboard tool
    Moodle->>LTI: GET /lti/login
    LTI->>Redis: Store nonce with TTL
    LTI-->>Moodle: Redirect to Moodle OIDC flow
    Moodle->>LTI: POST /lti/launch with signed JWT
    LTI->>Redis: Validate nonce
    LTI->>DB: Resolve user, role, and permissions
    LTI-->>Advisor: Redirect to advising dashboard
```

## 9. Sequence: Nightly ETL And At-Risk Processing

```mermaid
sequenceDiagram
    participant Beat as Celery Beat
    participant Worker as Celery Worker
    participant Moodle as Moodle REST API
    participant DB as MySQL Analytics
    participant AI as AI Gateway

    Beat->>Worker: Start nightly ETL
    Worker->>Moodle: Fetch login, submission, quiz, and forum data
    Moodle-->>Worker: Engagement data
    Worker->>DB: Upsert analytics projection
    Worker->>DB: Load SIS and Moodle risk signals
    Worker->>DB: Classify severity by configured rules
    alt Medium or High severity
        Worker->>AI: Generate advisor-facing explanation
        AI-->>Worker: Explanation text
        Worker->>DB: Store at-risk alert and ai_audit_log
    else Low or no risk
        Worker->>DB: Update resolved alerts if needed
    end
```

## 10. Sequence: Wellbeing Check-In

```mermaid
sequenceDiagram
    actor Student
    participant UI as React App
    participant API as Django API
    participant Rules as Rules Engine
    participant WDB as Restricted Wellbeing Schema
    participant Notify as Notification Service

    Student->>UI: Submit wellbeing check-in
    UI->>API: POST /api/v1/ai/wellbeing/triage
    API->>Rules: Evaluate mood rating and keyword rules
    Rules-->>API: Triage class
    API->>WDB: Store check-in and restricted audit metadata
    alt Escalate
        API->>Notify: Alert wellbeing_coordinator
        API-->>UI: Show crisis contacts and escalation message
    else Concerning
        API-->>UI: Show curated support resources
    else Normal
        API-->>UI: Show self-care resources
    end
```

## 11. Activity: Student Enrollment

```mermaid
flowchart TD
    A([Start]) --> B[Student selects section]
    B --> C{Registration window open?}
    C -- No --> X[Reject with clear reason]
    C -- Yes --> D{Prerequisites met?}
    D -- No --> X
    D -- Yes --> E{Capacity available?}
    E -- Yes --> F[Create enrollment]
    E -- No --> G{Waitlist enabled?}
    G -- No --> Y[Reject as full]
    G -- Yes --> H[Create waitlist entry]
    F --> I[Queue Moodle sync]
    H --> J[Notify student of waitlist position]
    I --> K([End])
    J --> K
    X --> K
    Y --> K
```

## 12. Activity: Wellbeing Triage

```mermaid
flowchart TD
    A([Start]) --> B[Student opens wellbeing check-in]
    B --> C{Opt-in consent enabled?}
    C -- No --> X[Hide feature and return to settings]
    C -- Yes --> D[Collect mood rating and optional text]
    D --> E[Apply deterministic rules]
    E --> F{Triage class}
    F -- Normal --> G[Store record and show self-care resources]
    F -- Concerning --> H[Store record and show support resources]
    F -- Escalate --> I[Store record and alert wellbeing coordinator]
    I --> J[Show crisis contacts]
    G --> K([End])
    H --> K
    J --> K
    X --> K
```

## 13. State: Grade Record Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> UnderReview: Faculty submits
    UnderReview --> Draft: Returned for correction
    UnderReview --> Official: Admin marks official
    Official --> SyncedToMoodle: Pass-back succeeds
    Official --> SyncFailed: Pass-back fails
    SyncFailed --> SyncedToMoodle: Retry succeeds
    Official --> ChangedAfterRelease: Approved grade change
    ChangedAfterRelease --> SyncedToMoodle: Updated grade synced
```

## 14. State: Enrollment Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Requested
    Requested --> Enrolled: Checks pass
    Requested --> Waitlisted: Section full and waitlist enabled
    Requested --> Rejected: Window closed or validation fails
    Waitlisted --> Enrolled: Promoted
    Waitlisted --> Removed: Student leaves waitlist
    Enrolled --> Dropped: Student or admin drop
    Enrolled --> Completed: Semester closes
```

## 15. Deployment Diagram

```mermaid
flowchart TB
    subgraph Internet["Institutional Network / Internet"]
        Users[Browsers]
        MoodleUsers[Moodle Users]
    end

    subgraph VM["Linux VM"]
        Proxy[Reverse Proxy]
        Frontend[Frontend Container]
        API[Backend API Container]
        Worker[Celery Worker Container]
        Beat[Celery Beat Container]
        Redis[(Redis Container)]
        MySQL[(MySQL Container)]
        Qdrant[(Qdrant Container)]
    end

    subgraph External["External Dependencies"]
        Moodle[Moodle Instance]
        AIGateway[AI Gateway]
        Storage[S3-compatible Storage]
        Mail[Email Service]
    end

    Users --> Proxy
    Proxy --> Frontend
    Proxy --> API
    API --> MySQL
    API --> Redis
    API --> Qdrant
    API --> Moodle
    API --> AIGateway
    API --> Storage
    API --> Mail

    Beat --> Worker
    Worker --> Redis
    Worker --> MySQL
    Worker --> Qdrant
    Worker --> Moodle
    Worker --> AIGateway
    Worker --> Mail

    MoodleUsers --> Moodle
```

## Notes

- The `wellbeing_coordinator` is a capability overlay, not a fifth primary role.
- Lane A and Lane B intentionally describe different integration mechanisms and should not be collapsed into one generic sync narrative.
- The at-risk engine uses rules to determine severity and uses the LLM only for explanation text.
- Wellbeing workflows are approval-gated and use stricter storage and audit boundaries than the rest of the AI layer.
- The ERD remains the authoritative domain model reference for entity design.
