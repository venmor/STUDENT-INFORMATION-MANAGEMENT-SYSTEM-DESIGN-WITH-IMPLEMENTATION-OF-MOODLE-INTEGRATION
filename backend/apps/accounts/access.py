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
