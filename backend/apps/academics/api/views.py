from __future__ import annotations

from django.http import HttpResponse
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.audit import record_access_event
from apps.accounts.constants import AccessEventType, RoleCode
from apps.academics.models import (
    AttendanceRecord,
    AttendanceSession,
    Course,
    CoursePrerequisite,
    CourseSection,
    CourseSectionStatus,
    Enrollment,
    EnrollmentStatus,
    GradeRecord,
    GradeStatus,
)
from apps.academics.services import (
    approve_enrollment,
    commit_bulk_enrollment,
    commit_grade_upload,
    create_enrollment,
    create_enrollment_pending,
    drop_enrollment,
    generate_exam_slip_pdf,
    generate_grade_template_csv,
    generate_results_slip_pdf,
    generate_transcript_pdf,
    officialise_grade,
    parse_bulk_enrollment_csv,
    parse_grade_upload_csv,
    preview_bulk_enrollment,
    preview_grade_upload,
    record_grade,
    reject_enrollment,
    transfer_enrollment,
    update_grade,
)
from apps.students.models import StudentProfile

from .serializers import (
    AttendanceSessionCreateSerializer,
    BulkEnrollmentFileSerializer,
    CourseSectionSerializer,
    CourseSerializer,
    EnrollmentCreateSerializer,
    EnrollmentSerializer,
    EnrollmentTransferSerializer,
    GradeCreateSerializer,
    GradeRecordSerializer,
    GradeUpdateSerializer,
    PrerequisiteCreateSerializer,
    SectionRosterEntrySerializer,
)


def require_admin(user):
    if user.primary_role != RoleCode.ADMIN:
        raise PermissionDenied("Admin access is required.")


def require_faculty_or_admin_for_section(user, section: CourseSection):
    if user.primary_role == RoleCode.ADMIN:
        return
    if user.primary_role == RoleCode.FACULTY and section.faculty_user_id == user.id:
        return
    raise PermissionDenied("Faculty assignment is required.")


def get_student_for_request(request, student_user_id: int | None) -> StudentProfile:
    if request.user.primary_role == RoleCode.STUDENT:
        return request.user.student_profile
    if student_user_id is None:
        raise PermissionDenied("A target student is required.")
    return get_object_or_404(StudentProfile.objects.select_related("user"), user_id=student_user_id)


def get_visible_courses_queryset(user):
    queryset = Course.objects.order_by("course_code").filter(is_active=True)
    if user.primary_role == RoleCode.STUDENT:
        student = getattr(user, "student_profile", None)
        if student is None:
            return queryset.none()
        return queryset.filter(programme_code__in=["", student.programme])
    return queryset


def get_visible_sections_queryset(user):
    queryset = (
        CourseSection.objects.select_related("course", "faculty_user")
        .prefetch_related("timetables")
        .filter(status=CourseSectionStatus.ACTIVE)
        .order_by("course__course_code", "section_code")
    )
    if user.primary_role == RoleCode.ADMIN:
        return queryset
    if user.primary_role == RoleCode.FACULTY:
        return queryset.filter(faculty_user=user)
    if user.primary_role == RoleCode.STUDENT:
        student = getattr(user, "student_profile", None)
        if student is None:
            return queryset.none()
        return queryset.filter(course__programme_code__in=["", student.programme]).distinct()
    if user.primary_role == RoleCode.ADVISOR:
        return queryset.filter(
            enrollments__student__advisor_assignments__advisor_user=user,
            enrollments__student__advisor_assignments__is_current=True,
            enrollments__is_active=True,
            enrollments__enrollment_status=EnrollmentStatus.ENROLLED,
        ).distinct()
    return queryset.none()


def get_visible_enrollments_queryset(user):
    queryset = (
        Enrollment.objects.select_related("student__user", "section__course", "section__faculty_user")
        .order_by("-enrolled_at", "-updated_at")
    )
    if user.primary_role == RoleCode.ADMIN:
        return queryset
    if user.primary_role == RoleCode.ADVISOR:
        return queryset.filter(
            student__advisor_assignments__advisor_user=user,
            student__advisor_assignments__is_current=True,
        ).distinct()
    if user.primary_role == RoleCode.STUDENT:
        return queryset.filter(student__user=user)
    return queryset.none()


def get_visible_grades_queryset(user):
    queryset = (
        GradeRecord.objects.select_related("student__user", "section__course", "section__faculty_user")
        .order_by("student__student_number", "section__course__course_code")
    )
    if user.primary_role == RoleCode.ADMIN:
        return queryset
    if user.primary_role == RoleCode.FACULTY:
        return queryset.filter(section__faculty_user=user)
    if user.primary_role == RoleCode.ADVISOR:
        return queryset.filter(
            student__advisor_assignments__advisor_user=user,
            student__advisor_assignments__is_current=True,
            grade_status=GradeStatus.OFFICIAL,
        ).distinct()
    if user.primary_role == RoleCode.STUDENT:
        return queryset.filter(student__user=user, grade_status=GradeStatus.OFFICIAL)
    return queryset.none()


class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.order_by("course_code")
    serializer_class = CourseSerializer

    def get_queryset(self):
        return get_visible_courses_queryset(self.request.user)

    def perform_create(self, serializer):
        require_admin(self.request.user)
        course = serializer.save()
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=self.request.user,
            request=self.request,
            view_name="courses-list-create",
            status_code=201,
            metadata={"entity": "course", "action": "create", "course_id": str(course.id)},
        )


class CourseDetailView(generics.RetrieveUpdateAPIView):
    queryset = Course.objects.order_by("course_code")
    serializer_class = CourseSerializer
    lookup_url_kwarg = "course_id"

    def get_queryset(self):
        return get_visible_courses_queryset(self.request.user)

    def update(self, request, *args, **kwargs):
        require_admin(request.user)
        response = super().update(request, *args, **kwargs)
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            request=request,
            view_name="course-detail",
            status_code=response.status_code,
            metadata={"entity": "course", "action": "update", "course_id": str(self.get_object().id)},
        )
        return response


class CoursePrerequisiteCreateView(APIView):
    def post(self, request, course_id):
        require_admin(request.user)
        course = get_object_or_404(Course, pk=course_id)
        serializer = PrerequisiteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prerequisite = CoursePrerequisite.objects.create(course=course, **serializer.validated_data)
        return Response({"id": str(prerequisite.id), "prerequisite_course_id": str(prerequisite.prerequisite_course_id)}, status=status.HTTP_201_CREATED)


class SectionCreateView(generics.ListCreateAPIView):
    queryset = CourseSection.objects.select_related("course")
    serializer_class = CourseSectionSerializer

    def get_queryset(self):
        return get_visible_sections_queryset(self.request.user)

    def perform_create(self, serializer):
        require_admin(self.request.user)
        section = serializer.save()
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=self.request.user,
            request=self.request,
            view_name="sections-list-create",
            status_code=201,
            metadata={"entity": "section", "action": "create", "section_id": str(section.id)},
        )


class SectionDetailView(generics.RetrieveUpdateAPIView):
    queryset = CourseSection.objects.select_related("course", "faculty_user").prefetch_related("timetables")
    serializer_class = CourseSectionSerializer
    lookup_url_kwarg = "section_id"

    def get_queryset(self):
        return get_visible_sections_queryset(self.request.user)

    def update(self, request, *args, **kwargs):
        require_admin(request.user)
        response = super().update(request, *args, **kwargs)
        record_access_event(
            event_type=AccessEventType.API_ACTION,
            actor_user=request.user,
            request=request,
            view_name="section-detail",
            status_code=response.status_code,
            metadata={"entity": "section", "action": "update", "section_id": str(self.get_object().id)},
        )
        return response


class SectionRosterView(APIView):
    def get(self, request, section_id):
        section = get_object_or_404(
            CourseSection.objects.select_related("course", "faculty_user"),
            pk=section_id,
        )
        require_faculty_or_admin_for_section(request.user, section)
        roster = (
            section.enrollments.filter(
                is_active=True,
                enrollment_status=EnrollmentStatus.ENROLLED,
            )
            .select_related("student__user")
            .order_by("student__student_number")
        )
        return Response(SectionRosterEntrySerializer(roster, many=True).data, status=status.HTTP_200_OK)


class EnrollmentCreateView(APIView):
    def get(self, request):
        queryset = get_visible_enrollments_queryset(request.user)
        student_id = request.query_params.get("student_id")
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        section_id = request.query_params.get("section_id")
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        include_inactive = request.query_params.get("include_inactive", "").lower() in {"1", "true", "yes", "on"}
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        return Response(EnrollmentSerializer(queryset, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = EnrollmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        section = get_object_or_404(CourseSection, pk=serializer.validated_data["section_id"])
        student = get_student_for_request(request, serializer.validated_data.get("student_user_id"))
        try:
            enrollment = create_enrollment(
                student=student,
                section=section,
                actor_user=request.user,
                actor_role=request.user.primary_role,
                allow_waitlist=serializer.validated_data["waitlist_if_full"],
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)


class EnrollmentDropView(APIView):
    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment.objects.select_related("student__user", "section"), pk=enrollment_id)
        if request.user.primary_role == RoleCode.STUDENT and enrollment.student.user_id != request.user.id:
            raise PermissionDenied("Students may only drop their own enrollments.")
        try:
            enrollment = drop_enrollment(enrollment=enrollment, actor_user=request.user, actor_role=request.user.primary_role, reason=request.data.get("reason", ""))
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_200_OK)


class EnrollmentTransferView(APIView):
    def post(self, request, enrollment_id):
        require_admin(request.user)
        enrollment = get_object_or_404(Enrollment.objects.select_related("student__user", "section"), pk=enrollment_id)
        serializer = EnrollmentTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_section = get_object_or_404(CourseSection, pk=serializer.validated_data["target_section_id"])
        try:
            transferred = transfer_enrollment(enrollment=enrollment, target_section=target_section, actor_user=request.user, actor_role=request.user.primary_role)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)
        return Response(EnrollmentSerializer(transferred).data, status=status.HTTP_200_OK)


class BulkEnrollmentPreviewView(APIView):
    def post(self, request):
        require_admin(request.user)
        serializer = BulkEnrollmentFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rows = parse_bulk_enrollment_csv(serializer.validated_data["file"])
        preview_rows, errors = preview_bulk_enrollment(rows)
        return Response({"preview_rows": preview_rows, "error_count": len(errors), "errors": errors}, status=status.HTTP_200_OK)


class BulkEnrollmentCommitView(APIView):
    def post(self, request):
        require_admin(request.user)
        serializer = BulkEnrollmentFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rows = parse_bulk_enrollment_csv(serializer.validated_data["file"])
        created, errors = commit_bulk_enrollment(rows, actor_user=request.user, actor_role=request.user.primary_role)
        return Response({"created_count": len(created), "error_count": len(errors), "errors": errors}, status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST)


class AttendanceSessionCreateView(APIView):
    def post(self, request):
        serializer = AttendanceSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        section = get_object_or_404(CourseSection, pk=serializer.validated_data["section_id"])
        require_faculty_or_admin_for_section(request.user, section)
        attendance_session = AttendanceSession.objects.create(section=section, session_date=serializer.validated_data["session_date"], recorded_by_user=request.user)
        for record in serializer.validated_data["records"]:
            student = get_object_or_404(StudentProfile, pk=record["student_id"])
            AttendanceRecord.objects.create(attendance_session=attendance_session, student=student, status=record["status"])
        return Response({"id": str(attendance_session.id)}, status=status.HTTP_201_CREATED)


class GradeCreateView(APIView):
    def get(self, request):
        queryset = get_visible_grades_queryset(request.user)
        student_id = request.query_params.get("student_id")
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return Response(GradeRecordSerializer(queryset, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GradeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = get_object_or_404(StudentProfile.objects.select_related("user"), user_id=serializer.validated_data["student_user_id"])
        section = get_object_or_404(CourseSection, pk=serializer.validated_data["section_id"])
        require_faculty_or_admin_for_section(request.user, section)
        try:
            grade_record = record_grade(
                student=student,
                section=section,
                actor_user=request.user,
                numeric_score=serializer.validated_data.get("numeric_score"),
                ca_score=serializer.validated_data.get("ca_score"),
                exam_score=serializer.validated_data.get("exam_score"),
                special_code=serializer.validated_data.get("special_code", ""),
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)
        return Response(GradeRecordSerializer(grade_record).data, status=status.HTTP_201_CREATED)


class GradeDetailView(APIView):
    def patch(self, request, grade_id):
        require_admin(request.user)
        grade_record = get_object_or_404(GradeRecord, pk=grade_id)
        serializer = GradeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            updated = update_grade(grade_record=grade_record, actor_user=request.user, numeric_score=serializer.validated_data.get("numeric_score"), special_code=serializer.validated_data.get("special_code", ""), reason=serializer.validated_data.get("change_reason", ""))
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)
        return Response(GradeRecordSerializer(updated).data, status=status.HTTP_200_OK)


class GradeOfficialiseView(APIView):
    def post(self, request, grade_id):
        require_admin(request.user)
        grade_record = get_object_or_404(GradeRecord, pk=grade_id)
        officialised = officialise_grade(grade_record=grade_record, actor_user=request.user)
        return Response(GradeRecordSerializer(officialised).data, status=status.HTTP_200_OK)


class TranscriptView(APIView):
    def get(self, request, student_id):
        student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=student_id)
        if request.user.primary_role == RoleCode.STUDENT and student.user_id != request.user.id:
            raise PermissionDenied("Students may only view their own transcript.")
        if request.user.primary_role == RoleCode.ADVISOR and not student.advisor_assignments.filter(advisor_user=request.user, is_current=True).exists():
            raise PermissionDenied("Advisor assignment is required.")
        pdf_bytes = generate_transcript_pdf(student)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="transcript-{student.student_number}.pdf"'
        return response


class PendingRegistrationCreateView(APIView):
    def post(self, request):
        serializer = EnrollmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        section = get_object_or_404(CourseSection, pk=serializer.validated_data["section_id"])
        student = get_student_for_request(request, serializer.validated_data.get("student_user_id"))
        try:
            enrollment = create_enrollment_pending(
                student=student,
                section=section,
                actor_user=request.user,
                actor_role=request.user.primary_role,
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)


class PendingRegistrationsListView(APIView):
    def get(self, request):
        if request.user.primary_role not in (RoleCode.ADVISOR, RoleCode.ADMIN):
            raise PermissionDenied("Advisor or admin access is required.")
        queryset = (
            Enrollment.objects.filter(
                enrollment_status=EnrollmentStatus.PENDING_APPROVAL,
                is_active=True,
            )
            .select_related("student__user", "section__course", "section__faculty_user")
            .order_by("-enrolled_at")
        )
        if request.user.primary_role == RoleCode.ADVISOR:
            queryset = queryset.filter(
                student__advisor_assignments__advisor_user=request.user,
                student__advisor_assignments__is_current=True,
            ).distinct()
        return Response(EnrollmentSerializer(queryset, many=True).data, status=status.HTTP_200_OK)


class PendingRegistrationApproveView(APIView):
    def post(self, request, enrollment_id):
        if request.user.primary_role not in (RoleCode.ADVISOR, RoleCode.ADMIN):
            raise PermissionDenied("Advisor or admin access is required.")
        enrollment = get_object_or_404(
            Enrollment.objects.select_related("student__user", "section__course"),
            pk=enrollment_id,
        )
        try:
            enrollment = approve_enrollment(enrollment=enrollment, actor_user=request.user)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_200_OK)


class PendingRegistrationRejectView(APIView):
    def post(self, request, enrollment_id):
        if request.user.primary_role not in (RoleCode.ADVISOR, RoleCode.ADMIN):
            raise PermissionDenied("Advisor or admin access is required.")
        enrollment = get_object_or_404(
            Enrollment.objects.select_related("student__user", "section__course"),
            pk=enrollment_id,
        )
        reason = request.data.get("reason", "")
        try:
            enrollment = reject_enrollment(enrollment=enrollment, actor_user=request.user, reason=reason)
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_200_OK)


class ExamSlipView(APIView):
    def get(self, request, student_id):
        student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=student_id)
        if request.user.primary_role == RoleCode.STUDENT and student.user_id != request.user.id:
            raise PermissionDenied("Students may only view their own exam slip.")
        semester = request.query_params.get("semester", "")
        academic_year = request.query_params.get("academic_year", "")
        if not semester or not academic_year:
            raise ValidationError("semester and academic_year query params are required.")
        pdf_bytes = generate_exam_slip_pdf(student, semester, academic_year)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="exam-slip-{student.student_number}.pdf"'
        return response


class ResultsSlipView(APIView):
    def get(self, request, student_id):
        student = get_object_or_404(StudentProfile.objects.select_related("user"), pk=student_id)
        if request.user.primary_role == RoleCode.STUDENT and student.user_id != request.user.id:
            raise PermissionDenied("Students may only view their own results slip.")
        semester = request.query_params.get("semester", "")
        academic_year = request.query_params.get("academic_year", "")
        if not semester or not academic_year:
            raise ValidationError("semester and academic_year query params are required.")
        pdf_bytes = generate_results_slip_pdf(student, semester, academic_year)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="results-slip-{student.student_number}.pdf"'
        return response


class GradeTemplateView(APIView):
    def get(self, request, section_id):
        section = get_object_or_404(CourseSection.objects.select_related("course"), pk=section_id)
        require_faculty_or_admin_for_section(request.user, section)
        csv_content = generate_grade_template_csv(section)
        response = HttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="grade-template-{section.course.course_code}-{section.section_code}.csv"'
        return response


class GradeUploadPreviewView(APIView):
    def post(self, request, section_id):
        section = get_object_or_404(CourseSection.objects.select_related("course"), pk=section_id)
        require_faculty_or_admin_for_section(request.user, section)
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            raise ValidationError("A CSV file is required.")
        rows = parse_grade_upload_csv(uploaded_file)
        preview_rows, errors = preview_grade_upload(rows, section)
        return Response({"preview_rows": preview_rows, "error_count": len(errors), "errors": errors}, status=status.HTTP_200_OK)


class GradeUploadCommitView(APIView):
    def post(self, request, section_id):
        section = get_object_or_404(CourseSection.objects.select_related("course"), pk=section_id)
        require_faculty_or_admin_for_section(request.user, section)
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            raise ValidationError("A CSV file is required.")
        rows = parse_grade_upload_csv(uploaded_file)
        created, errors = commit_grade_upload(rows, section, actor_user=request.user)
        return Response(
            {"created_count": len(created), "error_count": len(errors), "errors": errors},
            status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST,
        )
