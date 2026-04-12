# Modern SIS ERD Draft

This ERD is a domain-model baseline for schema design. It is intentionally focused on the entities required by SRS v1.1 and the Phase 1 to Phase 3 delivery path.

```mermaid
erDiagram
    USERS {
        uuid id PK
        string full_name
        string email
        string password_hash
        string primary_role
        boolean is_active
        boolean must_reset_password
        datetime last_login_at
        datetime created_at
    }

    USER_CAPABILITIES {
        uuid id PK
        uuid user_id FK
        string capability_name
        uuid granted_by_user_id FK
        datetime granted_at
        datetime revoked_at
    }

    STUDENTS {
        uuid id PK
        uuid user_id FK
        string student_number
        string national_id
        date date_of_birth
        string gender
        string programme
        int year_of_study
        string academic_standing
        boolean is_active
        datetime created_at
    }

    ADVISOR_ASSIGNMENTS {
        uuid id PK
        uuid student_id FK
        uuid advisor_user_id FK
        date effective_from
        date effective_to
        boolean is_current
    }

    FINANCIAL_FLAGS {
        uuid id PK
        uuid student_id FK
        string flag_type
        string reason
        date effective_date
        date cleared_date
        uuid created_by_user_id FK
        datetime created_at
    }

    ADVISING_NOTES {
        uuid id PK
        uuid student_id FK
        uuid created_by_user_id FK
        string status
        text note_text
        uuid approved_by_user_id FK
        datetime approved_at
        datetime created_at
        datetime updated_at
    }

    COURSES {
        uuid id PK
        string course_code
        string course_title
        string department
        int credit_hours
        text description
        boolean is_active
    }

    COURSE_PREREQUISITES {
        uuid id PK
        uuid course_id FK
        uuid prerequisite_course_id FK
    }

    COURSE_SECTIONS {
        uuid id PK
        uuid course_id FK
        string section_code
        uuid faculty_user_id FK
        string room
        string day_of_week
        time start_time
        time end_time
        string semester
        string academic_year
        int max_capacity
        string status
    }

    ENROLLMENTS {
        uuid id PK
        uuid student_id FK
        uuid section_id FK
        string enrollment_status
        string actor_role
        uuid actor_user_id FK
        datetime enrolled_at
        datetime dropped_at
    }

    WAITLIST_ENTRIES {
        uuid id PK
        uuid student_id FK
        uuid section_id FK
        int queue_position
        datetime joined_at
        uuid promoted_by_user_id FK
        datetime promoted_at
    }

    ATTENDANCE_SESSIONS {
        uuid id PK
        uuid section_id FK
        date session_date
        uuid recorded_by_user_id FK
        datetime created_at
    }

    ATTENDANCE_RECORDS {
        uuid id PK
        uuid attendance_session_id FK
        uuid student_id FK
        string status
        datetime recorded_at
    }

    GRADE_RECORDS {
        uuid id PK
        uuid student_id FK
        uuid section_id FK
        decimal numeric_score
        string letter_grade
        decimal grade_points
        string grade_status
        string special_code
        uuid entered_by_user_id FK
        uuid officialised_by_user_id FK
        datetime entered_at
        datetime officialised_at
    }

    MOODLE_USER_MAP {
        uuid id PK
        uuid user_id FK
        bigint moodle_user_id
        datetime synced_at
    }

    MOODLE_COURSE_MAP {
        uuid id PK
        uuid section_id FK
        bigint moodle_course_id
        datetime synced_at
    }

    AI_AUDIT_LOG {
        uuid id PK
        string feature_name
        uuid user_id FK
        uuid student_id FK
        string session_id
        text input_payload
        text output_payload
        text human_approved_version
        string provider_name
        string model_name
        string model_version
        datetime created_at
    }

    AT_RISK_ALERTS {
        uuid id PK
        uuid student_id FK
        string severity
        json active_signals
        text explanation
        boolean acknowledged
        uuid acknowledged_by_user_id FK
        datetime acknowledged_at
        datetime created_at
        datetime closed_at
    }

    WELLBEING_CHECKINS {
        uuid id PK
        uuid student_id FK
        int mood_rating
        text free_text
        string triage_class
        datetime submitted_at
        datetime deleted_at
    }

    WELLBEING_AUDIT_LOG {
        uuid id PK
        uuid student_id FK
        string triage_class
        string notification_status
        string actor_identifier
        datetime created_at
    }

    USERS ||--o| STUDENTS : has_student_profile
    USERS ||--o{ USER_CAPABILITIES : receives
    STUDENTS ||--o{ ADVISOR_ASSIGNMENTS : assigned
    USERS ||--o{ ADVISOR_ASSIGNMENTS : advises
    STUDENTS ||--o{ FINANCIAL_FLAGS : has
    STUDENTS ||--o{ ADVISING_NOTES : has
    USERS ||--o{ ADVISING_NOTES : creates
    COURSES ||--o{ COURSE_SECTIONS : offers
    COURSES ||--o{ COURSE_PREREQUISITES : requires
    COURSE_SECTIONS }o--|| USERS : taught_by
    STUDENTS ||--o{ ENROLLMENTS : has
    COURSE_SECTIONS ||--o{ ENROLLMENTS : contains
    STUDENTS ||--o{ WAITLIST_ENTRIES : queues
    COURSE_SECTIONS ||--o{ WAITLIST_ENTRIES : accepts
    COURSE_SECTIONS ||--o{ ATTENDANCE_SESSIONS : schedules
    ATTENDANCE_SESSIONS ||--o{ ATTENDANCE_RECORDS : captures
    STUDENTS ||--o{ ATTENDANCE_RECORDS : receives
    STUDENTS ||--o{ GRADE_RECORDS : earns
    COURSE_SECTIONS ||--o{ GRADE_RECORDS : issues
    USERS ||--o{ MOODLE_USER_MAP : maps
    COURSE_SECTIONS ||--o{ MOODLE_COURSE_MAP : maps
    STUDENTS ||--o{ AT_RISK_ALERTS : triggers
    STUDENTS ||--o{ WELLBEING_CHECKINS : submits
    STUDENTS ||--o{ WELLBEING_AUDIT_LOG : references
    USERS ||--o{ AI_AUDIT_LOG : initiates
```

## Notes

- `STUDENTS` is separated from `USERS` so institutional student attributes do not leak into non-student accounts.
- `ADVISOR_ASSIGNMENTS` is modeled historically, even though only one assignment is current at a time.
- `GRADE_RECORDS` keeps both numeric and derived grade state so transcript generation stays deterministic.
- `USER_CAPABILITIES` is how the `wellbeing_coordinator` access boundary is enforced without breaking the one-primary-role model.
- `WELLBEING_CHECKINS` and `WELLBEING_AUDIT_LOG` are intentionally separated from `AI_AUDIT_LOG`.
