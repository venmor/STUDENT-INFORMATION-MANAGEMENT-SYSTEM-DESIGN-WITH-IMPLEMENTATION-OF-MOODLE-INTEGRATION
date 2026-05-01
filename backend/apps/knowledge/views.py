from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import KnowledgeIngestionRun, KnowledgeSource
from .serializers import (
    KnowledgeIngestionRunSerializer,
    KnowledgeRetrievalResultSerializer,
    KnowledgeSourceSerializer,
    KnowledgeSummarySerializer,
    KnowledgeTestQuerySerializer,
)
from .services import knowledge_summary, test_knowledge_retrieval


class AdminKnowledgeSummaryView(APIView):
    def get(self, request):
        return Response(KnowledgeSummarySerializer(knowledge_summary()).data, status=status.HTTP_200_OK)


class AdminKnowledgeSourceListView(APIView):
    def get(self, request):
        sources = KnowledgeSource.objects.prefetch_related("chunks").order_by("source_type", "title")
        return Response(KnowledgeSourceSerializer(sources, many=True).data, status=status.HTTP_200_OK)


class AdminKnowledgeIngestionRunListView(APIView):
    def get(self, request):
        runs = KnowledgeIngestionRun.objects.order_by("-started_at", "-id")[:50]
        return Response(KnowledgeIngestionRunSerializer(runs, many=True).data, status=status.HTTP_200_OK)


class AdminKnowledgeTestQueryView(APIView):
    def post(self, request):
        serializer = KnowledgeTestQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        results = test_knowledge_retrieval(
            serializer.validated_data["query"],
            limit=serializer.validated_data.get("limit", 5),
            source_type=serializer.validated_data.get("sourceType", ""),
            actor=request.user,
            request=request,
        )
        return Response(
            {
                "query": serializer.validated_data["query"],
                "generatedAnswer": None,
                "results": KnowledgeRetrievalResultSerializer(results, many=True).data,
            },
            status=status.HTTP_200_OK,
        )
