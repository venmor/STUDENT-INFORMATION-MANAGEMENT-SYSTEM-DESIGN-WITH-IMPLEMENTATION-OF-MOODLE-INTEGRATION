from functools import wraps

from rest_framework.exceptions import NotAuthenticated, PermissionDenied


def require_role(required_role: str):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            user = request.user
            if not getattr(user, "is_authenticated", False):
                raise NotAuthenticated()
            if getattr(user, "primary_role", None) != required_role:
                raise PermissionDenied(f"Requires {required_role} role.")
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


def require_capability(required_capability: str, *, allowed_roles=None):
    allowed_role_set = set(allowed_roles or [])

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            user = request.user
            if not getattr(user, "is_authenticated", False):
                raise NotAuthenticated()
            if allowed_role_set and getattr(user, "primary_role", None) not in allowed_role_set:
                raise PermissionDenied("Primary role is not permitted for this capability.")
            if not user.has_capability(required_capability):
                raise PermissionDenied(f"Requires {required_capability} capability.")
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
