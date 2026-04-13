from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.constants import CapabilityName, RoleCode, STAFF_ROLE_CODES
from apps.accounts.permissions import require_capability, require_role

from .serializers import ModernSISTokenObtainPairSerializer, ModernSISTokenRefreshSerializer


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ModernSISTokenObtainPairSerializer


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ModernSISTokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@require_role(RoleCode.ADVISOR)
def advisor_probe(request):
    return Response({"detail": "advisor access granted"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@require_capability(
    CapabilityName.WELLBEING_COORDINATOR,
    allowed_roles=STAFF_ROLE_CODES,
)
def wellbeing_probe(request):
    return Response({"detail": "wellbeing access granted"}, status=status.HTTP_200_OK)

