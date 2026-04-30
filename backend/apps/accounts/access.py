from dataclasses import dataclass
from types import MappingProxyType

from django.urls import URLPattern, URLResolver, get_resolver

from .constants import CapabilityName, RoleCode, STAFF_ROLE_CODES


ALL_PRIMARY_ROLE_CODES = frozenset(RoleCode.values)


@dataclass(frozen=True, slots=True)
class AccessPolicy:
    allowed_roles: frozenset[str]
    required_capability: str | None = None

    def permits(self, user) -> bool:
        primary_role = getattr(user, "primary_role", None)
        if primary_role not in self.allowed_roles:
            return False
        if self.required_capability is None:
            return True
        return user.has_capability(self.required_capability)


PUBLIC_API_ROUTE_NAMES = frozenset(
    {
        "auth-login",
        "auth-refresh",
    }
)


PROTECTED_API_ROUTE_POLICIES = MappingProxyType(
    {
        "auth-probe-advisor": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
        "auth-probe-wellbeing": AccessPolicy(
            allowed_roles=frozenset(STAFF_ROLE_CODES),
            required_capability=CapabilityName.WELLBEING_COORDINATOR,
        ),
        "users-list-create": AccessPolicy(allowed_roles=frozenset({RoleCode.ADMIN})),
        "user-detail": AccessPolicy(allowed_roles=frozenset({RoleCode.ADMIN})),
        "user-deactivate": AccessPolicy(allowed_roles=frozenset({RoleCode.ADMIN})),
        "user-reset-password": AccessPolicy(allowed_roles=frozenset({RoleCode.ADMIN})),
        "user-access-logs": AccessPolicy(allowed_roles=frozenset({RoleCode.ADMIN})),
        "user-change-password": AccessPolicy(allowed_roles=ALL_PRIMARY_ROLE_CODES),
        "students-list-create": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN, RoleCode.ADVISOR})
        ),
        "student-detail": AccessPolicy(
            allowed_roles=frozenset({RoleCode.STUDENT, RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
        "student-deactivate": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "student-advisor-assignment-create": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "student-financial-flags": AccessPolicy(
            allowed_roles=frozenset({RoleCode.STUDENT, RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
        "student-financial-flag-detail": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "student-advising-notes": AccessPolicy(
            allowed_roles=frozenset({RoleCode.STUDENT, RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
        "student-advising-note-detail": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
        "student-advising-note-approve": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "student-correction-requests": AccessPolicy(
            allowed_roles=frozenset({RoleCode.STUDENT, RoleCode.ADMIN})
        ),
        "student-correction-request-detail": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "courses-list-create": AccessPolicy(allowed_roles=ALL_PRIMARY_ROLE_CODES),
        "course-detail": AccessPolicy(allowed_roles=ALL_PRIMARY_ROLE_CODES),
        "course-prerequisites-create": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "sections-list-create": AccessPolicy(allowed_roles=ALL_PRIMARY_ROLE_CODES),
        "section-detail": AccessPolicy(allowed_roles=ALL_PRIMARY_ROLE_CODES),
        "section-roster": AccessPolicy(
            allowed_roles=frozenset({RoleCode.FACULTY, RoleCode.ADMIN})
        ),
        "enrollments-create": AccessPolicy(
            allowed_roles=frozenset({RoleCode.STUDENT, RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
        "enrollments-bulk-preview": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "enrollments-bulk-commit": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "enrollment-drop": AccessPolicy(
            allowed_roles=frozenset({RoleCode.STUDENT, RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
        "enrollment-transfer": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "attendance-session-create": AccessPolicy(
            allowed_roles=frozenset({RoleCode.FACULTY, RoleCode.ADMIN})
        ),
        "grades-create": AccessPolicy(allowed_roles=ALL_PRIMARY_ROLE_CODES),
        "grade-detail": AccessPolicy(allowed_roles=frozenset({RoleCode.ADMIN})),
        "grade-officialise": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "student-transcript": AccessPolicy(
            allowed_roles=frozenset({RoleCode.STUDENT, RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
        "moodle-sync-summary": AccessPolicy(allowed_roles=frozenset({RoleCode.ADMIN})),
        "moodle-sync-outbox-events": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "moodle-sync-outbox-event-retry": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "moodle-sync-user-maps": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "moodle-sync-course-maps": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "moodle-sync-engagement-runs": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "moodle-sync-engagement-snapshots": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADMIN})
        ),
        "notifications-list": AccessPolicy(allowed_roles=ALL_PRIMARY_ROLE_CODES),
        "notifications-summary": AccessPolicy(allowed_roles=ALL_PRIMARY_ROLE_CODES),
        "notification-read": AccessPolicy(allowed_roles=ALL_PRIMARY_ROLE_CODES),
        "notifications-read-all": AccessPolicy(allowed_roles=ALL_PRIMARY_ROLE_CODES),
    }
)


def iter_named_api_route_names(urlpatterns, prefix: str = "") -> set[str]:
    route_names: set[str] = set()
    for pattern in urlpatterns:
        route = f"{prefix}{pattern.pattern}"
        if isinstance(pattern, URLPattern):
            if route.startswith("api/v1/") and pattern.name:
                route_names.add(pattern.name)
            continue
        if isinstance(pattern, URLResolver):
            route_names.update(iter_named_api_route_names(pattern.url_patterns, route))
    return route_names


def get_named_api_route_names() -> set[str]:
    return iter_named_api_route_names(get_resolver().url_patterns)
