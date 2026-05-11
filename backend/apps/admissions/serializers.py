from rest_framework import serializers

from apps.admissions.models import ApplicantDocument, ApplicantProfile


class ApplicantDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantDocument
        fields = ["id", "document_type", "file", "original_filename", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class ApplicantProfileSerializer(serializers.ModelSerializer):
    documents = ApplicantDocumentSerializer(many=True, read_only=True)
    programme_name = serializers.CharField(source="programme_applied.name", read_only=True, default=None)

    class Meta:
        model = ApplicantProfile
        fields = [
            "id", "email", "full_name", "national_id", "date_of_birth",
            "gender", "phone_number", "programme_applied", "programme_name",
            "application_status", "review_notes", "reviewed_at",
            "documents", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "application_status", "review_notes", "reviewed_at", "created_at", "updated_at"]


class ApplicantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantProfile
        fields = [
            "email", "full_name", "national_id", "date_of_birth",
            "gender", "phone_number", "programme_applied",
        ]


class ApplicationReviewSerializer(serializers.Serializer):
    review_notes = serializers.CharField(required=False, allow_blank=True, default="")
