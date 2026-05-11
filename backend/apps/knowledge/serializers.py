from __future__ import annotations

from rest_framework import serializers

from .models import KnowledgeIngestionRun, KnowledgeSource


class KnowledgeSourceSerializer(serializers.ModelSerializer):
    sourceType = serializers.CharField(source="source_type")
    sourcePath = serializers.CharField(source="source_path")
    checksumSha256 = serializers.CharField(source="checksum_sha256")
    chunkCount = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = KnowledgeSource
        fields = (
            "id",
            "sourceType",
            "title",
            "description",
            "sourcePath",
            "status",
            "visibility",
            "checksumSha256",
            "metadata",
            "chunkCount",
            "createdAt",
            "updatedAt",
        )

    def get_chunkCount(self, obj: KnowledgeSource) -> int:
        return obj.chunks.count()


class KnowledgeIngestionRunSerializer(serializers.ModelSerializer):
    startedAt = serializers.DateTimeField(source="started_at")
    completedAt = serializers.DateTimeField(source="completed_at", allow_null=True)
    sourcesProcessed = serializers.IntegerField(source="sources_processed")
    chunksCreated = serializers.IntegerField(source="chunks_created")
    chunksUpserted = serializers.IntegerField(source="chunks_upserted")
    failureCount = serializers.IntegerField(source="failure_count")
    lastError = serializers.CharField(source="last_error")

    class Meta:
        model = KnowledgeIngestionRun
        fields = (
            "id",
            "status",
            "startedAt",
            "completedAt",
            "sourcesProcessed",
            "chunksCreated",
            "chunksUpserted",
            "failureCount",
            "lastError",
            "metadata",
        )


class KnowledgeSummarySerializer(serializers.Serializer):
    sources = serializers.IntegerField()
    chunks = serializers.IntegerField()
    latestIngestion = KnowledgeIngestionRunSerializer(allow_null=True)
    vectorStore = serializers.DictField()


class KnowledgeTestQuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=500)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=10, default=5)
    sourceType = serializers.CharField(required=False, allow_blank=True)


class KnowledgeRetrievalResultSerializer(serializers.Serializer):
    chunkId = serializers.CharField()
    sourceId = serializers.CharField()
    sourceTitle = serializers.CharField()
    sourceType = serializers.CharField()
    score = serializers.FloatField()
    text = serializers.CharField()
