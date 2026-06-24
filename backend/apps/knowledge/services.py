from __future__ import annotations

import hashlib
import logging
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditCategory, AuditSeverity
from apps.audit.services import record_audit_event_safely, sanitize_audit_metadata

from .chunking import chunk_text
from .embeddings import get_embedding_provider
from .models import (
    KnowledgeChunk,
    KnowledgeIngestionRun,
    KnowledgeIngestionRunStatus,
    KnowledgeSource,
    KnowledgeSourceStatus,
    KnowledgeSourceType,
    KnowledgeSourceVisibility,
)
from .vector_store import VectorStoreUnavailable, get_vector_store


logger = logging.getLogger(__name__)


DEMO_SOURCES = [
    {
        "source_type": KnowledgeSourceType.REGISTRATION_PROCEDURES,
        "title": "Registration Procedures",
        "description": "Demo local registration procedure guide for retrieval testing.",
        "content": (
            "Demo local source. Students register for courses through the SIS registration workflow. "
            "Registration opens and closes according to the academic calendar. Advisor assistance may be required for transfers or overloads."
        ),
    },
    {
        "source_type": KnowledgeSourceType.ACADEMIC_REGULATIONS,
        "title": "Academic Regulations",
        "description": "Demo local academic regulations overview.",
        "content": (
            "Demo local source. Academic standing is reviewed each semester using official grades, GPA, and programme rules. "
            "Students should contact the Registrar for official interpretations of regulations."
        ),
    },
    {
        "source_type": KnowledgeSourceType.FEE_SCHEDULE,
        "title": "Fee Schedule",
        "description": "Demo local fee schedule overview.",
        "content": (
            "Demo local source. Fee schedules and payment deadlines are published by the finance office each semester. "
            "This demo text is not an official bill or receipt."
        ),
    },
    {
        "source_type": KnowledgeSourceType.COURSE_CATALOG,
        "title": "Course Catalog Overview",
        "description": "Demo local course catalog overview.",
        "content": (
            "Demo local source. The course catalog lists course codes, titles, credit hours, departments, prerequisites, and active sections. "
            "Students should confirm section availability in SIS before registration."
        ),
    },
    {
        "source_type": KnowledgeSourceType.ACADEMIC_CALENDAR,
        "title": "Academic Calendar Deadline Guide",
        "description": "Demo local deadline guide for retrieval testing.",
        "content": (
            "Demo local source. The deadline to drop a course is the published drop deadline in the academic calendar for the relevant section "
            "or semester. Students must drop a course before that drop deadline through the standard registration workflow. "
            "After the deadline, students should contact the Registrar or an academic advisor because normal self-service dropping may be closed."
        ),
    },
]


def checksum_text(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


@transaction.atomic
def seed_demo_knowledge_sources(*, created_by=None) -> list[KnowledgeSource]:
    sources = []
    for item in DEMO_SOURCES:
        source, _ = KnowledgeSource.objects.update_or_create(
            source_type=item["source_type"],
            title=item["title"],
            defaults={
                "description": item["description"],
                "source_path": "local-demo",
                "content": item["content"],
                "status": KnowledgeSourceStatus.READY,
                "visibility": KnowledgeSourceVisibility.PUBLIC_STUDENT,
                "checksum_sha256": checksum_text(item["content"]),
                "metadata": sanitize_audit_metadata({"demo": True, "officialPolicy": False, "phase": "4.1"}),
                "created_by": created_by if getattr(created_by, "pk", None) else None,
            },
        )
        sources.append(source)
    return sources


def knowledge_sources_for_ingestion(*, source_id=None, source_type: str = "", limit: int | None = None):
    queryset = KnowledgeSource.objects.filter(status__in=[KnowledgeSourceStatus.READY, KnowledgeSourceStatus.INGESTED]).order_by("source_type", "title")
    if source_id:
        queryset = queryset.filter(pk=source_id)
    if source_type:
        queryset = queryset.filter(source_type=source_type)
    if limit:
        queryset = queryset[: max(0, limit)]
    return queryset


@transaction.atomic
def ingest_knowledge_base(
    *,
    source_id=None,
    source_type: str = "",
    rebuild: bool = False,
    dry_run: bool = False,
    limit: int | None = None,
    vector_store=None,
    actor=None,
    request=None,
) -> KnowledgeIngestionRun:
    # Knowledge ingestion keeps authoritative source text in MySQL and stores
    # only searchable chunk vectors in the configured vector store. This lets
    # the co-pilot cite source records without making Qdrant the source of truth.
    run = KnowledgeIngestionRun.objects.create(
        metadata=sanitize_audit_metadata(
            {
                "sourceId": str(source_id) if source_id else "",
                "sourceType": source_type,
                "rebuild": rebuild,
                "dryRun": dry_run,
                "limit": limit,
                "embeddingProvider": getattr(settings, "EMBEDDING_PROVIDER", "deterministic"),
            }
        )
    )
    provider = get_embedding_provider()
    store = vector_store or get_vector_store()
    last_error = ""

    try:
        if not dry_run:
            store.ensure_collection(vector_size=provider.dimension)
        for source in knowledge_sources_for_ingestion(source_id=source_id, source_type=source_type, limit=limit):
            try:
                run.sources_processed += 1
                if rebuild and not dry_run:
                    store.delete_source(str(source.id))
                    source.chunks.all().delete()
                chunks = chunk_text(
                    source.content,
                    chunk_tokens=int(getattr(settings, "KNOWLEDGE_CHUNK_TOKENS", 512)),
                    overlap_tokens=int(getattr(settings, "KNOWLEDGE_CHUNK_OVERLAP", 64)),
                )
                run.chunks_created += len(chunks)
                if dry_run:
                    continue
                chunk_records: list[KnowledgeChunk] = []
                for chunk in chunks:
                    record, _ = KnowledgeChunk.objects.update_or_create(
                        source=source,
                        chunk_index=chunk.chunk_index,
                        defaults={
                            "text": chunk.text,
                            "token_count": chunk.token_count,
                            "vector_id": f"{source.id}:{chunk.chunk_index}",
                            "metadata": sanitize_audit_metadata(
                                {
                                    "sourceId": str(source.id),
                                    "sourceTitle": source.title,
                                    "sourceType": source.source_type,
                                    "visibility": source.visibility,
                                    "chunkIndex": chunk.chunk_index,
                                }
                            ),
                        },
                    )
                    chunk_records.append(record)
                vectors = provider.embed_texts([chunk.text for chunk in chunk_records])
                payloads = [
                    {
                        "id": str(chunk.id),
                        "vector": vectors[index],
                        "text": chunk.text,
                        "metadata": {
                            **chunk.metadata,
                            "chunkId": str(chunk.id),
                            "sourceId": str(source.id),
                            "sourceTitle": source.title,
                            "sourceType": source.source_type,
                        },
                    }
                    for index, chunk in enumerate(chunk_records)
                ]
                run.chunks_upserted += store.upsert_chunks(payloads)
                source.status = KnowledgeSourceStatus.INGESTED
                source.checksum_sha256 = checksum_text(source.content)
                source.save(update_fields=["status", "checksum_sha256", "updated_at"])
                _record_knowledge_audit(
                    actor=actor,
                    action="KNOWLEDGE_SOURCE_INGESTED",
                    summary=f"Knowledge source {source.title} was ingested.",
                    target_type="KnowledgeSource",
                    target_id=str(source.id),
                    metadata={"sourceId": str(source.id), "sourceType": source.source_type, "chunkCount": len(chunks)},
                    request=request,
                )
            except Exception as exc:
                run.failure_count += 1
                last_error = str(exc)
                logger.exception("Knowledge ingestion failed for source %s", source.id)
                source.status = KnowledgeSourceStatus.FAILED
                source.save(update_fields=["status", "updated_at"])
    except Exception as exc:
        run.failure_count += 1
        last_error = str(exc)

    run.last_error = last_error[:2000]
    run.completed_at = timezone.now()
    if run.failure_count and run.sources_processed == 0:
        run.status = KnowledgeIngestionRunStatus.FAILED
    elif run.failure_count:
        run.status = KnowledgeIngestionRunStatus.PARTIAL
    else:
        run.status = KnowledgeIngestionRunStatus.SUCCEEDED
    run.save(
        update_fields=[
            "sources_processed",
            "chunks_created",
            "chunks_upserted",
            "failure_count",
            "last_error",
            "completed_at",
            "status",
        ]
    )
    if run.failure_count:
        _notify_admins_of_ingestion_failure(run)
    return run


def test_knowledge_retrieval(query: str, *, vector_store=None, limit: int = 5, source_type: str = "", actor=None, request=None) -> list[dict[str, Any]]:
    provider = get_embedding_provider()
    store = vector_store or get_vector_store()
    query_vector = provider.embed_text(query)
    results = store.search(query_vector, limit=limit, filters={"sourceType": source_type} if source_type else None)
    shaped = [
        {
            "chunkId": result["metadata"].get("chunkId") or result["id"],
            "sourceId": result["metadata"].get("sourceId", ""),
            "sourceTitle": result["metadata"].get("sourceTitle", ""),
            "sourceType": result["metadata"].get("sourceType", ""),
            "score": round(float(result.get("score") or 0), 4),
            "text": result.get("text", ""),
        }
        for result in results
    ]
    _record_knowledge_audit(
        actor=actor,
        action="KNOWLEDGE_RETRIEVAL_TESTED",
        summary="Admin tested institutional knowledge retrieval.",
        target_type="KnowledgeRetrieval",
        target_id="test-query",
        metadata={
            "queryLength": len(query or ""),
            "resultCount": len(shaped),
            "chunkIds": [row["chunkId"] for row in shaped],
            "sourceIds": [row["sourceId"] for row in shaped],
        },
        request=request,
    )
    return shaped


test_knowledge_retrieval.__test__ = False


def knowledge_summary() -> dict[str, Any]:
    store = get_vector_store()
    try:
        health = store.health_check()
    except VectorStoreUnavailable as exc:
        health = {"healthy": False, "message": str(exc), "provider": getattr(settings, "KNOWLEDGE_VECTOR_STORE_PROVIDER", "qdrant")}
    return {
        "sources": KnowledgeSource.objects.count(),
        "chunks": KnowledgeChunk.objects.count(),
        "latestIngestion": KnowledgeIngestionRun.objects.order_by("-started_at", "-id").first(),
        "vectorStore": {
            **health,
            "collection": getattr(settings, "QDRANT_COLLECTION", "modern_sis_knowledge"),
        },
    }


def _record_knowledge_audit(
    *,
    actor,
    action: str,
    summary: str,
    target_type: str,
    target_id: str,
    metadata: dict[str, Any],
    severity: str = AuditSeverity.INFO,
    request=None,
) -> None:
    record_audit_event_safely(
        actor=actor,
        category=AuditCategory.AI,
        action=action,
        summary=summary,
        target_type=target_type,
        target_id=target_id,
        severity=severity,
        metadata=sanitize_audit_metadata(metadata),
        request=request,
    )


def _notify_admins_of_ingestion_failure(run: KnowledgeIngestionRun) -> None:
    try:
        from apps.notifications.models import NotificationCategory, NotificationSeverity
        from apps.notifications.services import notify_admins, sanitize_text

        notify_admins(
            category=NotificationCategory.SYSTEM,
            severity=NotificationSeverity.ERROR,
            title="Knowledge ingestion needs attention",
            message=f"Knowledge ingestion run {run.id} finished with {run.failure_count} failures. {sanitize_text(run.last_error)[:300]}",
            action_label="Open AI Foundation",
            action_url="/admin/ai-foundation",
            source_type="KnowledgeIngestionRun",
            source_id=str(run.id),
            metadata={"runId": str(run.id), "status": run.status, "failureCount": run.failure_count},
        )
    except Exception:
        logger.exception("Failed to notify admins about knowledge ingestion failure %s", run.id)
