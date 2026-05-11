from __future__ import annotations

import json

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.audit.services import sanitize_audit_metadata
from apps.documents.models import DocumentType, DocumentVisibility, StudentDocument
from apps.documents.permissions import can_archive_document, can_download_document, can_review_document
from apps.documents.validators import validate_document_upload
from apps.students.models import StudentProfile


class DocumentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    fullName = serializers.CharField(source="full_name")


class StudentDocumentSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    documentType = serializers.CharField(source="document_type")
    originalFilename = serializers.CharField(source="original_filename")
    contentType = serializers.CharField(source="content_type")
    fileSize = serializers.IntegerField(source="file_size")
    uploadedBy = serializers.SerializerMethodField()
    reviewedBy = serializers.SerializerMethodField()
    reviewedAt = serializers.DateTimeField(source="reviewed_at", allow_null=True)
    reviewNote = serializers.CharField(source="review_note")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")
    canDownload = serializers.SerializerMethodField()
    canReview = serializers.SerializerMethodField()
    canArchive = serializers.SerializerMethodField()

    class Meta:
        model = StudentDocument
        fields = (
            "id",
            "student",
            "documentType",
            "title",
            "description",
            "originalFilename",
            "contentType",
            "fileSize",
            "visibility",
            "status",
            "uploadedBy",
            "reviewedBy",
            "reviewedAt",
            "reviewNote",
            "metadata",
            "createdAt",
            "updatedAt",
            "canDownload",
            "canReview",
            "canArchive",
        )

    def _request_user(self):
        request = self.context.get("request")
        return getattr(request, "user", None)

    def get_student(self, obj: StudentDocument):
        return {
            "id": str(obj.student_id),
            "studentNumber": obj.student.student_number,
            "fullName": obj.student.user.full_name or obj.student.user.username,
            "programme": obj.student.programme,
        }

    def get_uploadedBy(self, obj: StudentDocument):
        if obj.uploaded_by is None:
            return None
        return {
            "id": obj.uploaded_by_id,
            "username": obj.uploaded_by.username,
            "fullName": obj.uploaded_by.full_name or obj.uploaded_by.username,
        }

    def get_reviewedBy(self, obj: StudentDocument):
        if obj.reviewed_by is None:
            return None
        return {
            "id": obj.reviewed_by_id,
            "username": obj.reviewed_by.username,
            "fullName": obj.reviewed_by.full_name or obj.reviewed_by.username,
        }

    def get_canDownload(self, obj: StudentDocument) -> bool:
        user = self._request_user()
        return bool(user and can_download_document(user, obj))

    def get_canReview(self, obj: StudentDocument) -> bool:
        user = self._request_user()
        return bool(user and can_review_document(user, obj))

    def get_canArchive(self, obj: StudentDocument) -> bool:
        user = self._request_user()
        return bool(user and can_archive_document(user, obj))


class StudentDocumentCreateSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all(), required=False)
    documentType = serializers.ChoiceField(choices=DocumentType.choices)
    title = serializers.CharField(max_length=160)
    description = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(choices=DocumentVisibility.choices, required=False, default=DocumentVisibility.ADMIN_ONLY)
    metadata = serializers.JSONField(required=False)
    file = serializers.FileField()

    def validate_file(self, value):
        try:
            validate_document_upload(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        return value

    def validate_metadata(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError("Metadata must be valid JSON.") from exc
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be an object.")
        return sanitize_audit_metadata(value)

    def validate(self, attrs):
        attrs["title"] = attrs["title"].strip()
        if not attrs["title"]:
            raise serializers.ValidationError({"title": "Title is required."})
        attrs["description"] = attrs.get("description", "").strip()
        attrs["metadata"] = attrs.get("metadata", {})
        return attrs


class StudentDocumentUpdateSerializer(serializers.Serializer):
    documentType = serializers.ChoiceField(choices=DocumentType.choices, required=False)
    title = serializers.CharField(max_length=160, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(choices=DocumentVisibility.choices, required=False)
    metadata = serializers.JSONField(required=False)

    def validate_metadata(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise serializers.ValidationError("Metadata must be valid JSON.") from exc
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("Metadata must be an object.")
        return sanitize_audit_metadata(value)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided.")
        if "title" in attrs:
            attrs["title"] = attrs["title"].strip()
            if not attrs["title"]:
                raise serializers.ValidationError({"title": "Title is required."})
        if "description" in attrs:
            attrs["description"] = attrs["description"].strip()
        return attrs

    def service_fields(self) -> dict:
        mapping = {
            "documentType": "document_type",
            "title": "title",
            "description": "description",
            "visibility": "visibility",
            "metadata": "metadata",
        }
        return {mapping[key]: value for key, value in self.validated_data.items()}


class DocumentReviewSerializer(serializers.Serializer):
    reviewNote = serializers.CharField(required=False, allow_blank=True)

    @property
    def review_note(self) -> str:
        return self.validated_data.get("reviewNote", "").strip()


class DocumentSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    pendingReview = serializers.IntegerField()
    approved = serializers.IntegerField()
    rejected = serializers.IntegerField()
    archived = serializers.IntegerField()
    studentVisible = serializers.IntegerField()
    adminOnly = serializers.IntegerField()
    recentUploads = serializers.IntegerField()
    byType = serializers.DictField(child=serializers.IntegerField())
