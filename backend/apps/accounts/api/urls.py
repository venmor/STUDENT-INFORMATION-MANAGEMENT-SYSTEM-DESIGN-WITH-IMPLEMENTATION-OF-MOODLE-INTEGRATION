from django.urls import path

from .views import (
    ChangePasswordView,
    ImpersonateStartView,
    ImpersonateStopView,
    LoginView,
    RefreshView,
    UserAccessLogListView,
    UserDeactivateView,
    UserDetailView,
    UserListCreateView,
    UserResetPasswordView,
    advisor_probe,
)


urlpatterns = [
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/refresh", RefreshView.as_view(), name="auth-refresh"),
    path("auth/probes/advisor", advisor_probe, name="auth-probe-advisor"),
    path("users", UserListCreateView.as_view(), name="users-list-create"),
    path("users/change-password", ChangePasswordView.as_view(), name="user-change-password"),
    path("users/<int:pk>", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:user_id>/deactivate", UserDeactivateView.as_view(), name="user-deactivate"),
    path("users/<int:user_id>/reset-password", UserResetPasswordView.as_view(), name="user-reset-password"),
    path("users/<int:user_id>/access-logs", UserAccessLogListView.as_view(), name="user-access-logs"),
    path("admin/impersonate/<int:user_id>", ImpersonateStartView.as_view(), name="admin-impersonate-start"),
    path("admin/stop-impersonate", ImpersonateStopView.as_view(), name="admin-impersonate-stop"),
]
