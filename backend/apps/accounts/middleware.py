from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .access import PROTECTED_API_ROUTE_POLICIES, PUBLIC_API_ROUTE_NAMES, get_named_api_route_names


class APIAccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        resolver_match = getattr(request, "resolver_match", None)
        view_name = getattr(resolver_match, "view_name", None)
        if view_name not in get_named_api_route_names():
            return None

        if view_name in PUBLIC_API_ROUTE_NAMES:
            return None

        policy = PROTECTED_API_ROUTE_POLICIES.get(view_name)
        if policy is None:
            return JsonResponse(
                {"detail": "You do not have permission to perform this action."},
                status=403,
            )

        authentication_result = self._authenticate_request(request)
        if isinstance(authentication_result, JsonResponse):
            return authentication_result

        request.user, request.auth = authentication_result
        if not policy.permits(request.user):
            return JsonResponse(
                {"detail": "You do not have permission to perform this action."},
                status=403,
            )

        return None

    def _authenticate_request(self, request):
        try:
            authentication_result = self.jwt_authenticator.authenticate(request)
        except (InvalidToken, TokenError):
            authentication_result = None

        if authentication_result is None:
            return JsonResponse(
                {"detail": "Authentication credentials were not provided."},
                status=401,
            )

        return authentication_result
