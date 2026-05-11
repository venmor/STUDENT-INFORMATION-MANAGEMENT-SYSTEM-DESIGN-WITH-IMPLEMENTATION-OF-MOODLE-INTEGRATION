from __future__ import annotations

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.constants import RoleCode
from apps.documents.models import DocumentVisibility, StudentDocument
from apps.documents.permissions import can_view_document, can_view_student_documents
from apps.documents.selectors import apply_document_filters, visible_documents_for_user
from apps.documents.services import (
    approve_document,
    archive_document,
    get_document_summary,
    reject_document,
    require_download_permission,
    update_document,
    upload_document,
)
from apps.students.models import StudentProfile

from .serializers import (
    DocumentReviewSerializer,
    StudentDocumentCreateSerializer,
    StudentDocumentSerializer,
    StudentDocumentUpdateSerializer,
)


def require_not_faculty(user) -> None:
    if getattr(user, "primary_role", None) == RoleCode.FACULTY:
        raise PermissionDenied("Faculty users do not have access to student documents.")


def serialize_document(document: StudentDocument, request, *, status_code=status.HTTP_200_OK):
    return Response(StudentDocumentSerializer(document, context={"request": request}).data, status=status_code)


class DocumentListCreateView(generics.ListCreateAPIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StudentDocumentCreateSerializer
        return StudentDocumentSerializer

    def get_queryset(self):
        require_not_faculty(self.request.user)
        return apply_document_filters(visible_documents_for_user(self.request.user), self.request.query_params)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = StudentDocumentSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = StudentDocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.validated_data.get("student")
        if student is None:
            if request.user.primary_role != RoleCode.STUDENT or not hasattr(request.user, "student_profile"):
                raise PermissionDenied("A student record is required for document upload.")
            student = request.user.student_profile
        document = upload_document(
            actor=request.user,
            student=student,
            uploaded_file=serializer.validated_data["file"],
            document_type=serializer.validated_data["documentType"],
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
            visibility=serializer.validated_data.get("visibility"),
            metadata=serializer.validated_data.get("metadata", {}),
            request=request,
        )
        return serialize_document(document, request, status_code=status.HTTP_201_CREATED)


class DocumentSummaryView(APIView):
    def get(self, request):
        require_not_faculty(request.user)
        return Response(get_document_summary(request.user), status=status.HTTP_200_OK)


class DocumentDetailView(APIView):
    def get_document(self, request, document_id) -> StudentDocument:
        document = get_object_or_404(
            StudentDocument.objects.select_related("student__user", "uploaded_by", "reviewed_by"),
            pk=document_id,
        )
        if not can_view_document(request.user, document):
            raise PermissionDenied("You do not have permission to view this document.")
        return document

    def get(self, request, document_id):
        return serialize_document(self.get_document(request, document_id), request)

    def patch(self, request, document_id):
        document = self.get_document(request, document_id)
        serializer = StudentDocumentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = update_document(
            document=document,
            actor=request.user,
            fields=serializer.service_fields(),
            request=request,
        )
        return serialize_document(updated, request)


class DocumentDownloadView(APIView):
    def get(self, request, document_id):
        document = get_object_or_404(
            StudentDocument.objects.select_related("student__user", "uploaded_by", "reviewed_by"),
            pk=document_id,
        )
        require_download_permission(document=document, actor=request.user, request=request)
        return FileResponse(
            document.file.open("rb"),
            as_attachment=True,
            filename=document.original_filename,
            content_type=document.content_type,
        )


class DocumentApproveView(APIView):
    def post(self, request, document_id):
        document = get_object_or_404(StudentDocument.objects.select_related("student__user", "uploaded_by", "reviewed_by"), pk=document_id)
        serializer = DocumentReviewSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        return serialize_document(approve_document(document=document, actor=request.user, review_note=serializer.review_note, request=request), request)


class DocumentRejectView(APIView):
    def post(self, request, document_id):
        document = get_object_or_404(StudentDocument.objects.select_related("student__user", "uploaded_by", "reviewed_by"), pk=document_id)
        serializer = DocumentReviewSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        return serialize_document(reject_document(document=document, actor=request.user, review_note=serializer.review_note, request=request), request)


class DocumentArchiveView(APIView):
    def post(self, request, document_id):
        document = get_object_or_404(StudentDocument.objects.select_related("student__user", "uploaded_by", "reviewed_by"), pk=document_id)
        return serialize_document(archive_document(document=document, actor=request.user, request=request), request)


class StudentDocumentListCreateView(DocumentListCreateView):
    def get_student(self) -> StudentProfile:
        student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=self.kwargs["student_id"])
        if not can_view_student_documents(self.request.user, student):
            raise PermissionDenied("You do not have permission to view documents for this student.")
        return student

    def get_queryset(self):
        student = self.get_student()
        queryset = visible_documents_for_user(self.request.user).filter(student=student)
        return apply_document_filters(queryset, self.request.query_params)

    def create(self, request, *args, **kwargs):
        student = self.get_student()
        serializer = StudentDocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = upload_document(
            actor=request.user,
            student=student,
            uploaded_file=serializer.validated_data["file"],
            document_type=serializer.validated_data["documentType"],
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
            visibility=serializer.validated_data.get("visibility"),
            metadata=serializer.validated_data.get("metadata", {}),
            request=request,
        )
        return serialize_document(document, request, status_code=status.HTTP_201_CREATED)


class MyDocumentListCreateView(DocumentListCreateView):
    def get_student(self) -> StudentProfile:
        if self.request.user.primary_role != RoleCode.STUDENT or not hasattr(self.request.user, "student_profile"):
            raise PermissionDenied("A linked student profile is required.")
        return self.request.user.student_profile

    def get_queryset(self):
        student = self.get_student()
        queryset = visible_documents_for_user(self.request.user).filter(student=student)
        return apply_document_filters(queryset, self.request.query_params)

    def create(self, request, *args, **kwargs):
        student = self.get_student()
        serializer = StudentDocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = upload_document(
            actor=request.user,
            student=student,
            uploaded_file=serializer.validated_data["file"],
            document_type=serializer.validated_data["documentType"],
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
            visibility=serializer.validated_data.get("visibility", DocumentVisibility.STUDENT_VISIBLE),
            metadata=serializer.validated_data.get("metadata", {}),
            request=request,
        )
        return serialize_document(document, request, status_code=status.HTTP_201_CREATED)
