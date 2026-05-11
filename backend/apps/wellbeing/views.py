from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser

from .models import WellbeingCheckIn, WellbeingConsent
from .permissions import IsStudent, IsWellbeingCoordinator
from .serializers import (
    WellbeingCheckInSerializer,
    WellbeingConsentSerializer,
    WellbeingHistorySerializer,
)
from .services import process_wellbeing_checkin, set_wellbeing_consent, get_anonymized_mood_trends


class WellbeingConsentView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        consent, _ = WellbeingConsent.objects.get_or_create(student=request.user.student_profile)
        return Response(WellbeingConsentSerializer(consent).data)

    def post(self, request):
        is_enabled = request.data.get("is_enabled", False)
        consent = set_wellbeing_consent(request.user.student_profile, is_enabled)
        return Response(WellbeingConsentSerializer(consent).data)


class WellbeingTriageView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        consent = WellbeingConsent.objects.filter(student=request.user.student_profile, is_enabled=True).first()
        if not consent:
            return Response(
                {"detail": "Wellbeing check-in requires explicit opt-in."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = WellbeingCheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result_dict = process_wellbeing_checkin(
            student=request.user.student_profile,
            mood_rating=serializer.validated_data["mood_rating"],
            comment=serializer.validated_data.get("comment", ""),
        )

        return Response(result_dict, status=status.HTTP_201_CREATED)


class WellbeingHistoryView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        history = WellbeingCheckIn.objects.filter(
            student=request.user.student_profile,
            is_deleted_by_student=False
        ).order_by("-created_at")
        return Response(WellbeingHistorySerializer(history, many=True).data)


class WellbeingCheckInDeleteView(APIView):
    permission_classes = [IsStudent]

    def delete(self, request, checkin_id):
        try:
            checkin = WellbeingCheckIn.objects.get(
                id=checkin_id,
                student=request.user.student_profile,
                is_deleted_by_student=False
            )
            # AI-WBE-009: remove original mood values and free-text
            checkin.is_deleted_by_student = True
            checkin.comment = "[DELETED]"
            checkin.mood_rating = 0 # Wiping original value
            checkin.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except WellbeingCheckIn.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class WellbeingHistoryPurgeView(APIView):
    permission_classes = [IsStudent]

    def delete(self, request):
        WellbeingCheckIn.objects.filter(
            student=request.user.student_profile
        ).update(
            is_deleted_by_student=True,
            comment="[PURGED]",
            mood_rating=0
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class WellbeingCoordinatorAlertsView(APIView):
    permission_classes = [IsWellbeingCoordinator]

    def get(self, request):
        from .models import TriageClass
        alerts = WellbeingCheckIn.objects.filter(
            triage_class=TriageClass.ESCALATE,
            is_deleted_by_student=False
        ).select_related("student", "student__user").order_by("-created_at")

        data = [{
            "id": a.id,
            "student_name": a.student.user.full_name,
            "student_number": a.student.student_number,
            "mood_rating": a.mood_rating,
            "created_at": a.created_at,
        } for a in alerts]

        return Response(data)


class WellbeingReportingTrendsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        trends = get_anonymized_mood_trends()
        return Response(trends)
