from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StudentAnalyticsSnapshot
from .selectors import apply_snapshot_filters, etl_run_queryset, snapshot_queryset
from .serializers import AnalyticsETLRunSerializer, AnalyticsSummarySerializer, StudentAnalyticsSnapshotSerializer
from .services import get_analytics_summary


class AdminAnalyticsSummaryView(APIView):
    def get(self, request):
        serializer = AnalyticsSummarySerializer(get_analytics_summary())
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminAnalyticsSnapshotListView(APIView):
    def get(self, request):
        queryset = apply_snapshot_filters(snapshot_queryset(), request.query_params)
        serializer = StudentAnalyticsSnapshotSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminAnalyticsETLRunListView(APIView):
    def get(self, request):
        serializer = AnalyticsETLRunSerializer(etl_run_queryset()[:50], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminAnalyticsSnapshotDetailView(APIView):
    def get(self, request, snapshot_id):
        snapshot = get_object_or_404(
            StudentAnalyticsSnapshot.objects.select_related("student__user", "user", "source_run"),
            pk=snapshot_id,
        )
        return Response(StudentAnalyticsSnapshotSerializer(snapshot).data, status=status.HTTP_200_OK)
