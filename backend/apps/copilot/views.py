from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CopilotMessage
from .permissions import require_student_user
from .selectors import sessions_for_user
from .serializers import (
    CopilotFeedbackResponseSerializer,
    CopilotFeedbackSerializer,
    CopilotQuerySerializer,
    CopilotSessionCreateSerializer,
    CopilotSessionDetailSerializer,
    CopilotSessionSerializer,
    answer_to_payload,
)
from .services import (
    answer_copilot_question,
    archive_copilot_session,
    create_copilot_session,
    get_session_for_user_or_404,
    rate_copilot_message,
)


class CopilotQueryView(APIView):
    def post(self, request):
        require_student_user(request.user)
        serializer = CopilotQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = answer_copilot_question(
            user=request.user,
            question=serializer.validated_data["question"],
            session_id=serializer.validated_data.get("sessionId"),
            request=request,
        )
        return Response(answer_to_payload(answer), status=status.HTTP_200_OK)


class CopilotSessionListCreateView(APIView):
    def get(self, request):
        require_student_user(request.user)
        sessions = sessions_for_user(request.user)[:50]
        return Response(CopilotSessionSerializer(sessions, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        require_student_user(request.user)
        serializer = CopilotSessionCreateSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        session = create_copilot_session(
            user=request.user,
            title=serializer.validated_data.get("title", ""),
        )
        return Response(CopilotSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class CopilotSessionDetailView(APIView):
    def get(self, request, session_id):
        session = get_session_for_user_or_404(user=request.user, session_id=session_id)
        return Response(CopilotSessionDetailSerializer(session).data, status=status.HTTP_200_OK)


class CopilotSessionArchiveView(APIView):
    def post(self, request, session_id):
        session = archive_copilot_session(user=request.user, session_id=session_id)
        return Response(CopilotSessionSerializer(session).data, status=status.HTTP_200_OK)


class CopilotFeedbackView(APIView):
    def post(self, request, message_id):
        require_student_user(request.user)
        serializer = CopilotFeedbackSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        get_object_or_404(CopilotMessage.objects.select_related("session"), pk=message_id)
        feedback = rate_copilot_message(
            user=request.user,
            message_id=message_id,
            rating=serializer.validated_data["rating"],
            comment=serializer.validated_data.get("comment", ""),
        )
        return Response(CopilotFeedbackResponseSerializer(feedback).data, status=status.HTTP_201_CREATED)
