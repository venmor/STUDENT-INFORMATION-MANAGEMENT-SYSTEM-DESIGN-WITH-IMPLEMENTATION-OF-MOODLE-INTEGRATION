from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.audit import record_access_event
from apps.accounts.constants import AccessEventType, RoleCode
from apps.students.models import (
    AdvisorAssignment,
    AdvisingNote,
    AdvisingNoteStatus,
    FinancialFlag,
    StudentCorrectionRequest,
    StudentCorrectionRequestStatus,
    StudentProfile,
)

from .serializers import (
    AdvisorAssignmentSerializer,
    AdvisingNoteCreateSerializer,
    AdvisingNoteSerializer,
    AdvisingNoteUpdateSerializer,
    FinancialFlagSerializer,
    FinancialFlagUpdateSerializer,
    StudentCorrectionRequestCreateSerializer,
    StudentCorrectionRequestReviewSerializer,
    StudentCorrectionRequestSerializer,
    StudentProfileCreateSerializer,
    StudentProfileSerializer,
)


def serialise_audit_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    return value


def build_field_change_set(instance, validated_data: dict) -> dict[str, dict[str, object]]:
    changes: dict[str, dict[str, object]] = {}
    for field_name, updated_value in validated_data.items():
        previous_value = getattr(instance, field_name)
        if previous_value == updated_value:
            continue
        changes[field_name] = {
            "before": serialise_audit_value(previous_value),
            "after": serialise_audit_value(updated_value),
        }
    return changes


def can_view_student(user, student: StudentProfile) -> bool:
    if user.primary_role == RoleCode.ADMIN:
        return True
    if user.primary_role == RoleCode.STUDENT:
        return student.user_id == user.id
    if user.primary_role == RoleCode.ADVISOR:
        return student.advisor_assignments.filter(advisor_user=user, is_current=True).exists()
    return False


def require_admin(user):
    if user.primary_role != RoleCode.ADMIN:
        raise PermissionDenied("Admin access is required.")


def require_assigned_advisor_or_admin(user, student: StudentProfile):
    if user.primary_role == RoleCode.ADMIN:
        return
    if user.primary_role == RoleCode.ADVISOR and student.advisor_assignments.filter(advisor_user=user, is_current=True).exists():
        return
    raise PermissionDenied("Advisor assignment is required.")


def require_student_self_or_admin(user, student: StudentProfile):
    if user.primary_role == RoleCode.ADMIN:
        return
    if user.primary_role == RoleCode.STUDENT and student.user_id == user.id:
        return
    raise PermissionDenied("You do not have permission to access this correction workflow.")


class StudentListCreateView(generics.ListCreateAPIView):
    queryset = StudentProfile.objects.select_related("user").order_by("student_number")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StudentProfileCreateSerializer
        return StudentProfileSerializer

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        if self.request.user.primary_role == RoleCode.ADMIN:
            return queryset
        if self.request.user.primary_role == RoleCode.ADVISOR:
            return queryset.filter(advisor_assignments__advisor_user=self.request.user, advisor_assignments__is_current=True)
        raise PermissionDenied("You do not have permission to view students.")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)
        student_ids = [str(student_id) for student_id in queryset.values_list("id", flat=True)]
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            request=request,
            view_name="students-list-create",
            status_code=response.status_code,
            metadata={
                "entity": "student_profile",
                "action": "read_list",
                "student_count": len(student_ids),
                "student_ids": student_ids,
            },
        )
        return response

    def _record_student_created(self, student):
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=self.request.user,
            subject_user=student.user,
            request=self.request,
            view_name="students-list-create",
            status_code=201,
            metadata={"entity": "student_profile", "action": "create", "student_id": str(student.id)},
        )

    def perform_create(self, serializer):
        require_admin(self.request.user)
        student = serializer.save()
        self._record_student_created(student)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        require_admin(request.user)
        student = serializer.save()
        self._record_student_created(student)
        headers = self.get_success_headers(serializer.data)
        return Response(StudentProfileSerializer(student).data, status=status.HTTP_201_CREATED, headers=headers)


class StudentDetailView(generics.RetrieveUpdateAPIView):
    queryset = StudentProfile.objects.select_related("user")
    serializer_class = StudentProfileSerializer
    lookup_url_kwarg = "student_id"

    def get_serializer_class(self):
        if self.request.method in {"PATCH", "PUT"}:
            return StudentProfileSerializer
        return StudentProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        student = self.get_object()
        if not can_view_student(request.user, student):
            raise PermissionDenied("You do not have permission to view this student.")
        response = super().retrieve(request, *args, **kwargs)
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-detail",
            status_code=response.status_code,
            metadata={"entity": "student_profile", "action": "read", "student_id": str(student.id)},
        )
        return response

    def update(self, request, *args, **kwargs):
        require_admin(request.user)
        partial = kwargs.pop("partial", False)
        student = self.get_object()
        serializer = self.get_serializer(student, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        changes = build_field_change_set(student, serializer.validated_data)
        student = serializer.save()
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-detail",
            status_code=200,
            metadata={
                "entity": "student_profile",
                "action": "update",
                "student_id": str(student.id),
                "changes": changes,
            },
        )
        return Response(StudentProfileSerializer(student).data, status=status.HTTP_200_OK)


class StudentDeactivateView(APIView):
    def post(self, request, student_id):
        require_admin(request.user)
        student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=student_id)
        was_active = student.is_active
        if was_active:
            student.is_active = False
            student.save(update_fields=["is_active", "updated_at"])
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-deactivate",
            status_code=200,
            metadata={
                "entity": "student_profile",
                "action": "deactivate",
                "student_id": str(student.id),
                "changes": {"is_active": {"before": was_active, "after": False}},
            },
        )
        return Response({"detail": "Student record deactivated."}, status=status.HTTP_200_OK)


class AdvisorAssignmentCreateView(APIView):
    def post(self, request, student_id):
        require_admin(request.user)
        student = get_object_or_404(StudentProfile, pk=student_id)
        student.advisor_assignments.filter(is_current=True).update(is_current=False, effective_to=request.data.get("effective_from"))
        serializer = AdvisorAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = AdvisorAssignment.objects.create(student=student, **serializer.validated_data)
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-advisor-assignment-create",
            status_code=201,
            metadata={"entity": "advisor_assignment", "action": "create", "student_id": str(student.id)},
        )
        return Response(AdvisorAssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED)


class FinancialFlagListCreateView(generics.ListCreateAPIView):
    serializer_class = FinancialFlagSerializer

    def get_student(self):
        return get_object_or_404(StudentProfile.objects.select_related("user"), pk=self.kwargs["student_id"])

    def get_queryset(self):
        student = self.get_student()
        if not can_view_student(self.request.user, student):
            raise PermissionDenied("You do not have permission to view this student.")
        return student.financial_flags.order_by("-effective_date", "-created_at")

    def list(self, request, *args, **kwargs):
        student = self.get_student()
        queryset = self.get_queryset()
        response = super().list(request, *args, **kwargs)
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-financial-flags",
            status_code=response.status_code,
            metadata={
                "entity": "financial_flag",
                "action": "read_list",
                "student_id": str(student.id),
                "flag_count": queryset.count(),
            },
        )
        return response

    def perform_create(self, serializer):
        require_admin(self.request.user)
        student = self.get_student()
        serializer.save(student=student, created_by_user=self.request.user)
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=self.request.user,
            subject_user=student.user,
            request=self.request,
            view_name="student-financial-flags",
            status_code=201,
            metadata={"entity": "financial_flag", "action": "create", "student_id": str(student.id)},
        )


class FinancialFlagDetailView(APIView):
    def patch(self, request, student_id, flag_id):
        require_admin(request.user)
        student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=student_id)
        flag = get_object_or_404(FinancialFlag, pk=flag_id, student=student)
        serializer = FinancialFlagUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        changes = build_field_change_set(flag, serializer.validated_data)
        for field_name, value in serializer.validated_data.items():
            setattr(flag, field_name, value)
        flag.save(update_fields=list(serializer.validated_data.keys()))
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-financial-flag-detail",
            status_code=200,
            metadata={
                "entity": "financial_flag",
                "action": "update",
                "student_id": str(student.id),
                "flag_id": str(flag.id),
                "changes": changes,
            },
        )
        return Response(FinancialFlagSerializer(flag).data, status=status.HTTP_200_OK)


class AdvisingNoteListCreateView(generics.ListCreateAPIView):
    def get_student(self):
        return get_object_or_404(StudentProfile.objects.select_related("user"), pk=self.kwargs["student_id"])

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AdvisingNoteCreateSerializer
        return AdvisingNoteSerializer

    def get_queryset(self):
        student = self.get_student()
        if not can_view_student(self.request.user, student):
            raise PermissionDenied("You do not have permission to view this student.")
        queryset = student.advising_notes.order_by("-created_at")
        if self.request.user.primary_role == RoleCode.STUDENT:
            return queryset.filter(status=AdvisingNoteStatus.APPROVED)
        return queryset

    def list(self, request, *args, **kwargs):
        student = self.get_student()
        queryset = self.get_queryset()
        response = super().list(request, *args, **kwargs)
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-advising-notes",
            status_code=response.status_code,
            metadata={
                "entity": "advising_note",
                "action": "read_list",
                "student_id": str(student.id),
                "note_count": queryset.count(),
            },
        )
        return response

    def perform_create(self, serializer):
        student = self.get_student()
        require_assigned_advisor_or_admin(self.request.user, student)
        note = serializer.save(student=student, created_by_user=self.request.user)
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=self.request.user,
            subject_user=student.user,
            request=self.request,
            view_name="student-advising-notes",
            status_code=201,
            metadata={"entity": "advising_note", "action": "create", "student_id": str(student.id), "note_id": str(note.id)},
        )

    def create(self, request, *args, **kwargs):
        student = self.get_student()
        require_assigned_advisor_or_admin(request.user, student)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = serializer.save(student=student, created_by_user=request.user)
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-advising-notes",
            status_code=201,
            metadata={"entity": "advising_note", "action": "create", "student_id": str(student.id), "note_id": str(note.id)},
        )
        headers = self.get_success_headers(serializer.data)
        return Response(AdvisingNoteSerializer(note).data, status=status.HTTP_201_CREATED, headers=headers)


class AdvisingNoteApproveView(APIView):
    def post(self, request, student_id, note_id):
        require_admin(request.user)
        student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=student_id)
        note = get_object_or_404(AdvisingNote, pk=note_id, student=student)
        note.status = AdvisingNoteStatus.APPROVED
        note.approved_by_user = request.user
        note.approved_at = timezone.now()
        note.save(update_fields=["status", "approved_by_user", "approved_at", "updated_at"])
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-advising-note-approve",
            status_code=200,
            metadata={"entity": "advising_note", "action": "approve", "student_id": str(student.id), "note_id": str(note.id)},
        )
        return Response(AdvisingNoteSerializer(note).data, status=status.HTTP_200_OK)


class AdvisingNoteDetailView(APIView):
    def patch(self, request, student_id, note_id):
        student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=student_id)
        require_assigned_advisor_or_admin(request.user, student)
        note = get_object_or_404(AdvisingNote, pk=note_id, student=student)
        if note.status == AdvisingNoteStatus.APPROVED:
            return Response(
                {"detail": "Approved notes cannot be updated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AdvisingNoteUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        changes = build_field_change_set(note, serializer.validated_data)
        note.note_text = serializer.validated_data["note_text"]
        note.save(update_fields=["note_text", "updated_at"])
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-advising-note-detail",
            status_code=200,
            metadata={
                "entity": "advising_note",
                "action": "update",
                "student_id": str(student.id),
                "note_id": str(note.id),
                "changes": changes,
            },
        )
        return Response(AdvisingNoteSerializer(note).data, status=status.HTTP_200_OK)


class StudentCorrectionRequestListCreateView(generics.ListCreateAPIView):
    def get_student(self):
        return get_object_or_404(StudentProfile.objects.select_related("user"), pk=self.kwargs["student_id"])

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StudentCorrectionRequestCreateSerializer
        return StudentCorrectionRequestSerializer

    def get_queryset(self):
        student = self.get_student()
        require_student_self_or_admin(self.request.user, student)
        return student.correction_requests.order_by("-created_at", "-updated_at")

    def perform_create(self, serializer):
        student = self.get_student()
        require_student_self_or_admin(self.request.user, student)
        if self.request.user.primary_role != RoleCode.STUDENT:
            raise PermissionDenied("Only students may submit correction requests.")
        correction_request = serializer.save(student=student)
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=self.request.user,
            subject_user=student.user,
            request=self.request,
            view_name="student-correction-requests",
            status_code=201,
            metadata={
                "entity": "student_correction_request",
                "action": "create",
                "student_id": str(student.id),
                "correction_request_id": str(correction_request.id),
            },
        )

    def create(self, request, *args, **kwargs):
        student = self.get_student()
        require_student_self_or_admin(request.user, student)
        if request.user.primary_role != RoleCode.STUDENT:
            raise PermissionDenied("Only students may submit correction requests.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        correction_request = serializer.save(student=student)
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-correction-requests",
            status_code=201,
            metadata={
                "entity": "student_correction_request",
                "action": "create",
                "student_id": str(student.id),
                "correction_request_id": str(correction_request.id),
            },
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            StudentCorrectionRequestSerializer(correction_request).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class StudentCorrectionRequestDetailView(APIView):
    def patch(self, request, student_id, correction_request_id):
        require_admin(request.user)
        student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=student_id)
        correction_request = get_object_or_404(StudentCorrectionRequest, pk=correction_request_id, student=student)
        serializer = StudentCorrectionRequestReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        changes = build_field_change_set(correction_request, serializer.validated_data)
        correction_request.status = serializer.validated_data["status"]
        correction_request.review_note = serializer.validated_data.get("review_note", "")
        correction_request.reviewed_by_user = request.user
        correction_request.reviewed_at = timezone.now()
        correction_request.save(
            update_fields=["status", "review_note", "reviewed_by_user", "reviewed_at", "updated_at"]
        )
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            subject_user=student.user,
            request=request,
            view_name="student-correction-request-detail",
            status_code=200,
            metadata={
                "entity": "student_correction_request",
                "action": "review",
                "student_id": str(student.id),
                "correction_request_id": str(correction_request.id),
                "changes": changes,
                "review_status": correction_request.status,
            },
        )
        return Response(StudentCorrectionRequestSerializer(correction_request).data, status=status.HTTP_200_OK)
