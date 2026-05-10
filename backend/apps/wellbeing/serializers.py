from rest_framework import serializers

from .models import WellbeingCheckIn, WellbeingConsent


class WellbeingConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellbeingConsent
        fields = ["id", "is_enabled", "consented_at", "updated_at"]
        read_only_fields = ["id", "consented_at", "updated_at"]


class WellbeingCheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellbeingCheckIn
        fields = ["id", "mood_rating", "comment", "triage_class", "created_at"]
        read_only_fields = ["id", "triage_class", "created_at"]

    def validate_mood_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Mood rating must be between 1 and 5.")
        return value


class WellbeingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WellbeingCheckIn
        fields = ["id", "mood_rating", "triage_class", "created_at"]
        read_only_fields = ["id", "mood_rating", "triage_class", "created_at"]
