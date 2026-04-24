from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings

from apps.accounts.constants import CapabilityName
from apps.accounts.models import AccessLog, UserCapability


User = get_user_model()


class ModernSISTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        student_profile_id = None
        if hasattr(self.user, "student_profile"):
            student_profile_id = str(self.user.student_profile.id)
        return {
            "access_token": data["access"],
            "refresh_token": data["refresh"],
            "expires_in": int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
            "user": {
                "id": self.user.id,
                "username": self.user.username,
                "full_name": self.user.full_name,
                "primary_role": self.user.primary_role,
                "must_reset_password": self.user.must_reset_password,
                "student_profile_id": student_profile_id,
            },
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


class UserCapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCapability
        fields = ("capability_name", "granted_at")


class UserSerializer(serializers.ModelSerializer):
    capability_names = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "full_name",
            "primary_role",
            "is_active",
            "must_reset_password",
            "capability_names",
        )

    def get_capability_names(self, obj):
        return list(obj.capabilities.order_by("capability_name").values_list("capability_name", flat=True))


class UserCreateSerializer(serializers.ModelSerializer):
    temporary_password = serializers.CharField(write_only=True)
    capability_names = serializers.ListField(
        child=serializers.ChoiceField(choices=CapabilityName.choices),
        required=False,
        allow_empty=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "full_name",
            "primary_role",
            "temporary_password",
            "capability_names",
        )

    def validate_temporary_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("temporary_password")
        capability_names = validated_data.pop("capability_names", [])
        user = User.objects.create_user(password=password, **validated_data)
        user.must_reset_password = True
        user.save(update_fields=["must_reset_password"])
        for capability_name in capability_names:
            UserCapability.objects.create(user=user, capability_name=capability_name)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    capability_names = serializers.ListField(
        child=serializers.ChoiceField(choices=CapabilityName.choices),
        required=False,
        allow_empty=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = ("email", "full_name", "primary_role", "is_active", "must_reset_password", "capability_names")

    def update(self, instance, validated_data):
        capability_names = validated_data.pop("capability_names", None)
        instance = super().update(instance, validated_data)
        if capability_names is not None:
            instance.capabilities.exclude(capability_name__in=capability_names).delete()
            existing = set(instance.capabilities.values_list("capability_name", flat=True))
            for capability_name in capability_names:
                if capability_name not in existing:
                    UserCapability.objects.create(user=instance, capability_name=capability_name)
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_current_password(self, value):
        user = self.context["request"].user
        authenticated_user = authenticate(username=user.username, password=value)
        if authenticated_user is None:
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value, self.context["request"].user)
        return value


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        user = self.context["target_user"]
        validate_password(value, user)
        return value


class AccessLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.SerializerMethodField()
    subject_username = serializers.SerializerMethodField()

    class Meta:
        model = AccessLog
        fields = (
            "id",
            "event_type",
            "actor_username",
            "subject_username",
            "view_name",
            "request_path",
            "request_method",
            "response_status",
            "metadata",
            "created_at",
        )

    def get_actor_username(self, obj):
        return obj.actor_user.username if obj.actor_user else None

    def get_subject_username(self, obj):
        return obj.subject_user.username if obj.subject_user else None
