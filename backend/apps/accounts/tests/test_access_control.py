from apps.accounts.access import (
    PROTECTED_API_ROUTE_POLICIES,
    PUBLIC_API_ROUTE_NAMES,
    get_named_api_route_names,
)


def test_every_api_route_is_registered_with_public_or_protected_access():
    registered_route_names = set(PUBLIC_API_ROUTE_NAMES) | set(PROTECTED_API_ROUTE_POLICIES)
    api_route_names = get_named_api_route_names()

    assert api_route_names == registered_route_names
