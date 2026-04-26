from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.audit import record_access_event
from apps.accounts.constants import AccessEventType
from apps.accounts.models import AccessLog

from .serializers import (
    AccessLogSerializer,
    ChangePasswordSerializer,
    ModernSISTokenObtainPairSerializer,
    ModernSISTokenRefreshSerializer,
    ResetPasswordSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


User = get_user_model()


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ModernSISTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        username = request.data.get("username", "")
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            subject_user = User.objects.filter(username=username).first()
            record_access_event(
                event_type=AccessEventType.LOGIN_FAILURE,
                subject_user=subject_user,
                request=request,
                view_name="auth-login",
                status_code=401,
                metadata={"username": username},
            )
            raise

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        user = serializer.user
        record_access_event(
            event_type=AccessEventType.LOGIN_SUCCESS,
            actor_user=user,
            subject_user=user,
            request=request,
            view_name="auth-login",
            status_code=200,
        )
        return response


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ModernSISTokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def advisor_probe(request):
    return Response({"detail": "advisor access granted"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def wellbeing_probe(request):
    return Response({"detail": "wellbeing access granted"}, status=status.HTTP_200_OK)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.order_by("id")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer

    def _log_user_created(self, user):
        record_access_event(
            event_type=AccessEventType.USER_CREATED,
            actor_user=self.request.user,
            subject_user=user,
            request=self.request,
            view_name="users-list-create",
            status_code=201,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self._log_user_created(user)
        headers = self.get_success_headers(serializer.data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED, headers=headers)


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.order_by("id")

    def get_serializer_class(self):
        if self.request.method in {"PATCH", "PUT"}:
            return UserUpdateSerializer
        return UserSerializer

    def perform_update(self, serializer):
        user = serializer.save()
        record_access_event(
            event_type=AccessEventType.USER_UPDATED,
            actor_user=self.request.user,
            subject_user=user,
            request=self.request,
            view_name="user-detail",
            status_code=200,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        record_access_event(
            event_type=AccessEventType.USER_UPDATED,
            actor_user=request.user,
            subject_user=user,
            request=request,
            view_name="user-detail",
            status_code=200,
        )
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class UserDeactivateView(APIView):
    def post(self, request, user_id: int):
        user = get_object_or_404(User, pk=user_id)
        user.is_active = False
        user.save(update_fields=["is_active"])
        from apps.integration.services import create_sync_event

        create_sync_event(
            event_type="USER_SYNC_REQUESTED",
            payload={"user_id": user.id, "action": "SUSPEND"},
        )
        record_access_event(
            event_type=AccessEventType.USER_DEACTIVATED,
            actor_user=request.user,
            subject_user=user,
            request=request,
            view_name="user-deactivate",
            status_code=200,
        )
        return Response({"detail": "User deactivated."}, status=status.HTTP_200_OK)


class UserResetPasswordView(APIView):
    def post(self, request, user_id: int):
        user = get_object_or_404(User, pk=user_id)
        serializer = ResetPasswordSerializer(data=request.data, context={"target_user": user})
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data["new_password"])
        user.must_reset_password = True
        user.save(update_fields=["password", "must_reset_password"])
        record_access_event(
            event_type=AccessEventType.PASSWORD_RESET,
            actor_user=request.user,
            subject_user=user,
            request=request,
            view_name="user-reset-password",
            status_code=200,
        )
        return Response({"detail": "Password reset."}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.must_reset_password = False
        request.user.save(update_fields=["password", "must_reset_password"])
        record_access_event(
            event_type=AccessEventType.PASSWORD_CHANGE,
            actor_user=request.user,
            subject_user=request.user,
            request=request,
            view_name="user-change-password",
            status_code=200,
        )
        return Response({"detail": "Password updated."}, status=status.HTTP_200_OK)


class UserAccessLogListView(generics.ListAPIView):
    serializer_class = AccessLogSerializer

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["user_id"])
        return AccessLog.objects.filter(Q(actor_user=user) | Q(subject_user=user))
