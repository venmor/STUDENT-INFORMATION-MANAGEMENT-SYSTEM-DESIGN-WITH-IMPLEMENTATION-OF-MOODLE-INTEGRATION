from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class KnowledgeSourceType(models.TextChoices):
    ACADEMIC_CALENDAR = "ACADEMIC_CALENDAR", "Academic Calendar"
    COURSE_CATALOG = "COURSE_CATALOG", "Course Catalog"
    ACADEMIC_REGULATIONS = "ACADEMIC_REGULATIONS", "Academic Regulations"
    REGISTRATION_PROCEDURES = "REGISTRATION_PROCEDURES", "Registration Procedures"
    FEE_SCHEDULE = "FEE_SCHEDULE", "Fee Schedule"
    SYSTEM_POLICY = "SYSTEM_POLICY", "System Policy"
    OTHER = "OTHER", "Other"


class KnowledgeSourceStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    READY = "READY", "Ready"
    INGESTED = "INGESTED", "Ingested"
    FAILED = "FAILED", "Failed"


class KnowledgeSourceVisibility(models.TextChoices):
    PUBLIC_STUDENT = "PUBLIC_STUDENT", "Public Student"
    STAFF_ONLY = "STAFF_ONLY", "Staff Only"
    ADMIN_ONLY = "ADMIN_ONLY", "Admin Only"


class KnowledgeIngestionRunStatus(models.TextChoices):
    STARTED = "STARTED", "Started"
    SUCCEEDED = "SUCCEEDED", "Succeeded"
    FAILED = "FAILED", "Failed"
    PARTIAL = "PARTIAL", "Partial"


class KnowledgeSource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_type = models.CharField(max_length=40, choices=KnowledgeSourceType.choices)
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    source_path = models.CharField(max_length=500, blank=True)
    content = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=KnowledgeSourceStatus.choices, default=KnowledgeSourceStatus.DRAFT)
    visibility = models.CharField(
        max_length=24,
        choices=KnowledgeSourceVisibility.choices,
        default=KnowledgeSourceVisibility.PUBLIC_STUDENT,
    )
    checksum_sha256 = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_knowledge_sources",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["source_type", "title"]
        constraints = [
            models.UniqueConstraint(fields=["source_type", "title"], name="knowledge_unique_source_type_title")
        ]

    def __str__(self) -> str:
        return f"{self.source_type}:{self.title}"


class KnowledgeChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(KnowledgeSource, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.PositiveIntegerField()
    text = models.TextField()
    token_count = models.PositiveIntegerField(default=0)
    vector_id = models.CharField(max_length=128, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["source__title", "chunk_index"]
        constraints = [
            models.UniqueConstraint(fields=["source", "chunk_index"], name="knowledge_unique_chunk_per_source_index")
        ]

    def __str__(self) -> str:
        return f"{self.source.title}:{self.chunk_index}"


class KnowledgeIngestionRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=16, choices=KnowledgeIngestionRunStatus.choices, default=KnowledgeIngestionRunStatus.STARTED)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    sources_processed = models.PositiveIntegerField(default=0)
    chunks_created = models.PositiveIntegerField(default=0)
    chunks_upserted = models.PositiveIntegerField(default=0)
    failure_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-started_at", "id"]

    def __str__(self) -> str:
        return f"knowledge-ingestion:{self.status}:{self.started_at:%Y-%m-%d %H:%M:%S}"
