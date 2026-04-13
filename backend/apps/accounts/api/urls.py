from django.urls import path

from .views import LoginView, RefreshView, advisor_probe, wellbeing_probe


urlpatterns = [
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/refresh", RefreshView.as_view(), name="auth-refresh"),
    path("auth/probes/advisor", advisor_probe, name="auth-probe-advisor"),
    path("auth/probes/wellbeing", wellbeing_probe, name="auth-probe-wellbeing"),
]

