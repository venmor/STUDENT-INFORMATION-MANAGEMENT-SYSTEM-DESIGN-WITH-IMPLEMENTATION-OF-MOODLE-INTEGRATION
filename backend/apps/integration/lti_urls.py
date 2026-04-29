from django.urls import path

from . import lti_views


urlpatterns = [
    path("jwks", lti_views.jwks, name="lti-jwks"),
    path("login", lti_views.login, name="lti-login"),
    path("launch", lti_views.launch, name="lti-launch"),
    path("api/session", lti_views.session_context, name="lti-session-context"),
]
