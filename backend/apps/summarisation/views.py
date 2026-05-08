from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.students.models import StudentProfile

from .models import SummarisationRequest
from .serializers import SummariseApproveInputSerializer, SummariseInputSerializer, SummarisationOutputSerializer
from .services import approve_summarisation, create_summarisation_request


class SummariseView(APIView):
    def post(self, request):
        serializer = SummariseInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = None
        student_id = serializer.validated_data.get("student_id")
        if student_id:
            student = StudentProfile.objects.filter(id=student_id).first()
        summarisation = create_summarisation_request(
            user=request.user,
            raw_text=serializer.validated_data["raw_text"],
            student=student,
            request=request,
        )
        return Response(
            SummarisationOutputSerializer(summarisation).data,
            status=status.HTTP_201_CREATED,
        )


class SummariseApproveView(APIView):
    def post(self, request, summarisation_id):
        summarisation = SummarisationRequest.objects.filter(
            id=summarisation_id, user=request.user
        ).first()
        if not summarisation:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SummariseApproveInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        summarisation = approve_summarisation(
            user=request.user,
            summarisation=summarisation,
            human_edited_output=serializer.validated_data,
            request=request,
        )
        return Response(
            SummarisationOutputSerializer(summarisation).data,
            status=status.HTTP_200_OK,
        )
