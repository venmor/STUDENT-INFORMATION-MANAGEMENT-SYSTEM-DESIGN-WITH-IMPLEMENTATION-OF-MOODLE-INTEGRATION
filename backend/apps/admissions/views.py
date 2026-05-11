from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.admissions.models import ApplicantDocument, ApplicantProfile, ApplicationStatus
from apps.admissions.serializers import (
    ApplicantCreateSerializer,
    ApplicantDocumentSerializer,
    ApplicantProfileSerializer,
    ApplicationReviewSerializer,
)
from apps.admissions.services import approve_application, reject_application


class PublicApplicationCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ApplicantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        applicant = serializer.save()
        return Response(ApplicantProfileSerializer(applicant).data, status=status.HTTP_201_CREATED)


class PublicDocumentUploadView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, applicant_id):
        try:
            applicant = ApplicantProfile.objects.get(id=applicant_id)
        except ApplicantProfile.DoesNotExist:
            return Response({"detail": "Applicant not found."}, status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get("file")
        document_type = request.data.get("document_type", "OTHER")
        if not file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        doc = ApplicantDocument.objects.create(
            applicant=applicant,
            document_type=document_type,
            file=file,
            original_filename=file.name,
        )
        return Response(ApplicantDocumentSerializer(doc).data, status=status.HTTP_201_CREATED)


class PublicApplicationSubmitView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, applicant_id):
        try:
            applicant = ApplicantProfile.objects.get(id=applicant_id)
        except ApplicantProfile.DoesNotExist:
            return Response({"detail": "Applicant not found."}, status=status.HTTP_404_NOT_FOUND)

        if applicant.application_status != ApplicationStatus.DRAFT:
            return Response({"detail": "Application already submitted."}, status=status.HTTP_400_BAD_REQUEST)

        applicant.application_status = ApplicationStatus.SUBMITTED
        applicant.save()
        return Response(ApplicantProfileSerializer(applicant).data)


class AdminApplicationListView(generics.ListAPIView):
    serializer_class = ApplicantProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ApplicantProfile.objects.select_related("programme_applied").prefetch_related("documents")
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(application_status=status_filter)
        programme = self.request.query_params.get("programme")
        if programme:
            qs = qs.filter(programme_applied_id=programme)
        return qs


class AdminApplicationDetailView(generics.RetrieveAPIView):
    serializer_class = ApplicantProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ApplicantProfile.objects.select_related("programme_applied").prefetch_related("documents")
    lookup_field = "pk"
    lookup_url_kwarg = "applicant_id"


class AdminApplicationApproveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, applicant_id):
        if request.user.primary_role != "ADMIN":
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

        try:
            applicant = ApplicantProfile.objects.select_related("programme_applied").get(id=applicant_id)
        except ApplicantProfile.DoesNotExist:
            return Response({"detail": "Applicant not found."}, status=status.HTTP_404_NOT_FOUND)

        if applicant.application_status not in (ApplicationStatus.SUBMITTED, ApplicationStatus.UNDER_REVIEW):
            return Response({"detail": "Application not in reviewable state."}, status=status.HTTP_400_BAD_REQUEST)

        new_user = approve_application(applicant, reviewed_by=request.user)
        return Response({"detail": "Application approved.", "user_id": new_user.id}, status=status.HTTP_200_OK)


class AdminApplicationRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, applicant_id):
        if request.user.primary_role != "ADMIN":
            return Response({"detail": "Admin only."}, status=status.HTTP_403_FORBIDDEN)

        try:
            applicant = ApplicantProfile.objects.get(id=applicant_id)
        except ApplicantProfile.DoesNotExist:
            return Response({"detail": "Applicant not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ApplicationReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reject_application(applicant, reviewed_by=request.user, notes=serializer.validated_data.get("review_notes", ""))
        return Response({"detail": "Application rejected."}, status=status.HTTP_200_OK)
