from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings


class ModernSISTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return {
            "access_token": data["access"],
            "refresh_token": data["refresh"],
            "expires_in": int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
        }


class ModernSISTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        token_serializer = TokenRefreshSerializer(data={"refresh": attrs["refresh_token"]})
        token_serializer.is_valid(raise_exception=True)
        data = token_serializer.validated_data
        return {
            "access_token": data["access"],
            "refresh_token": data.get("refresh", attrs["refresh_token"]),
            "expires_in": int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
        }

