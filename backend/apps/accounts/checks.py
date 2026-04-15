from django.core.checks import Error, Tags, register

from .access import PUBLIC_API_ROUTE_NAMES, PROTECTED_API_ROUTE_POLICIES, get_named_api_route_names


@register(Tags.security)
def check_api_access_policy_coverage(app_configs, **kwargs):
    api_route_names = get_named_api_route_names()
    declared_route_names = set(PUBLIC_API_ROUTE_NAMES) | set(PROTECTED_API_ROUTE_POLICIES)

    errors = []
    missing_route_names = sorted(api_route_names - declared_route_names)
    if missing_route_names:
        errors.append(
            Error(
                "Every API route must declare public access or a protected access policy.",
                hint="Add the missing route names to PUBLIC_API_ROUTE_NAMES or PROTECTED_API_ROUTE_POLICIES.",
                obj="apps.accounts.access",
                id="accounts.E001",
            )
        )

    unused_route_names = sorted(declared_route_names - api_route_names)
    if unused_route_names:
        errors.append(
            Error(
                "The access policy registry contains route names that are not present in the API URL configuration.",
                hint="Remove stale route names from the access registry.",
                obj="apps.accounts.access",
                id="accounts.E002",
            )
        )

    return errors
