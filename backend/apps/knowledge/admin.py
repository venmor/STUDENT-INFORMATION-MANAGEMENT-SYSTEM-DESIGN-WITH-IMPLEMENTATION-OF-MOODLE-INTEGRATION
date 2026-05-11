from django.contrib import admin

from .models import KnowledgeChunk, KnowledgeIngestionRun, KnowledgeSource


@admin.register(KnowledgeSource)
class KnowledgeSourceAdmin(admin.ModelAdmin):
    list_display = ("title", "source_type", "visibility", "status", "updated_at")
    list_filter = ("source_type", "visibility", "status")
    search_fields = ("title", "description", "source_path")


@admin.register(KnowledgeChunk)
class KnowledgeChunkAdmin(admin.ModelAdmin):
    list_display = ("source", "chunk_index", "token_count", "vector_id", "created_at")
    search_fields = ("source__title", "text", "vector_id")


@admin.register(KnowledgeIngestionRun)
class KnowledgeIngestionRunAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "sources_processed", "chunks_created", "chunks_upserted", "failure_count", "started_at")
    list_filter = ("status",)
    search_fields = ("id", "last_error")
