# Step 4.3 Staff Workflow Acceleration (Summarisation) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add AI-powered note summarisation for advisors and admins per SRS Section 6.2 (AI-SUM-001 through AI-SUM-007).

**Architecture:** New `apps.summarisation` backend app with deterministic + OpenAI-compatible providers, reusing the existing `AIAuditLog` model from `apps.copilot`. The existing disabled `AISummarisationPanel` in the advisor student profile becomes live. A standalone `/admin/summarise` page gives admins student-free summarisation.

**Tech Stack:** Django REST Framework, OpenAI chat completions API (via existing provider pattern), React 18 + TypeScript + TanStack Query, Vitest + pytest.

---

## File Structure

### Backend — New files

| File | Responsibility |
|------|---------------|
| `backend/apps/summarisation/__init__.py` | Package marker |
| `backend/apps/summarisation/apps.py` | Django app config |
| `backend/apps/summarisation/models.py` | `SummarisationRequest` model + status/urgency enums |
| `backend/apps/summarisation/providers.py` | `DeterministicSummarisationProvider` + `OpenAISummarisationProvider` + factory |
| `backend/apps/summarisation/prompts.py` | System prompt for structured extraction |
| `backend/apps/summarisation/services.py` | Orchestration: validate → provider → audit → persist |
| `backend/apps/summarisation/serializers.py` | DRF input/output serializers |
| `backend/apps/summarisation/views.py` | `SummariseView` + `SummariseApproveView` |
| `backend/apps/summarisation/urls.py` | URL patterns under `ai/summarise/` |
| `backend/apps/summarisation/migrations/0001_initial.py` | Auto-generated migration |
| `backend/apps/summarisation/management/__init__.py` | Package marker |
| `backend/apps/summarisation/management/commands/__init__.py` | Package marker |
| `backend/apps/summarisation/management/commands/seed_summarisation_demo.py` | Demo seed data |
| `backend/apps/summarisation/tests/__init__.py` | Package marker |
| `backend/apps/summarisation/tests/test_services.py` | Service layer tests |
| `backend/apps/summarisation/tests/test_api.py` | API permission and integration tests |

### Backend — Modified files

| File | Change |
|------|--------|
| `backend/sis_backend/settings.py` | Add `apps.summarisation` to `INSTALLED_APPS` |
| `backend/sis_backend/urls.py` | Add `path("api/v1/", include("apps.summarisation.urls"))` |
| `backend/apps/accounts/access.py` | Add route policies for `summarise-request` and `summarise-approve` |
| `backend/apps/copilot/models.py` | Add `SUMMARISATION_REQUEST` and `SUMMARISATION_APPROVED` to `AIAuditAction` |

### Frontend — New files

| File | Responsibility |
|------|---------------|
| `frontend/src/hooks/useSummarisation.ts` | TanStack Query mutations for summarise + approve |
| `frontend/src/pages/admin/Summarise.tsx` | Standalone admin summarisation page |
| `frontend/src/features/summarisation/SummarisationForm.tsx` | Shared input form with char counter + governance notice |
| `frontend/src/features/summarisation/SummarisationResult.tsx` | Editable structured result form |

### Frontend — Modified files

| File | Change |
|------|--------|
| `frontend/src/components/advisor/AISummarisationPanel.tsx` | Replace disabled placeholder with live summarisation flow |
| `frontend/src/router.tsx` | Add `/admin/summarise` route |
| `frontend/src/components/layout/Sidebar.tsx` | Add "Summarise" link under admin Insights group |

---

## Task 1: Backend app scaffold and model

**Files:**
- Create: `backend/apps/summarisation/__init__.py`
- Create: `backend/apps/summarisation/apps.py`
- Create: `backend/apps/summarisation/models.py`
- Modify: `backend/sis_backend/settings.py:62`
- Modify: `backend/apps/copilot/models.py:33-38`

- [ ] **Step 1: Create app directory and config**

```bash
mkdir -p backend/apps/summarisation/management/commands
mkdir -p backend/apps/summarisation/tests
touch backend/apps/summarisation/__init__.py
touch backend/apps/summarisation/management/__init__.py
touch backend/apps/summarisation/management/commands/__init__.py
touch backend/apps/summarisation/tests/__init__.py
```

Create `backend/apps/summarisation/apps.py`:
```python
from django.apps import AppConfig


class SummarisationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.summarisation"
```

- [ ] **Step 2: Add AIAuditAction entries to copilot models**

In `backend/apps/copilot/models.py`, add to the `AIAuditAction` class after `COPILOT_RETRIEVAL_ONLY`:
```python
    SUMMARISATION_REQUEST = "SUMMARISATION_REQUEST", "Summarisation request"
    SUMMARISATION_APPROVED = "SUMMARISATION_APPROVED", "Summarisation approved"
```

- [ ] **Step 3: Create the SummarisationRequest model**

Create `backend/apps/summarisation/models.py`:
```python
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class SummarisationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    DISCARDED = "DISCARDED", "Discarded"


class UrgencyLevel(models.TextChoices):
    ROUTINE = "Routine", "Routine"
    FOLLOW_UP_NEEDED = "Follow-up Needed", "Follow-up Needed"
    URGENT = "Urgent", "Urgent"


class SummarisationRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summarisation_requests",
    )
    student = models.ForeignKey(
        "students.StudentProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="summarisation_requests",
    )
    raw_input_text = models.TextField()
    ai_output = models.JSONField(default=dict)
    human_edited_output = models.JSONField(null=True, blank=True)
    advising_note = models.ForeignKey(
        "students.AdvisingNote",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="summarisation_requests",
    )
    status = models.CharField(
        max_length=16,
        choices=SummarisationStatus.choices,
        default=SummarisationStatus.PENDING,
    )
    provider = models.CharField(max_length=40)
    model_name = models.CharField(max_length=120, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="summ_user_idx"),
            models.Index(fields=["student", "-created_at"], name="summ_student_idx"),
            models.Index(fields=["status", "-created_at"], name="summ_status_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.status}:{self.id}"
```

- [ ] **Step 4: Register app in settings**

In `backend/sis_backend/settings.py`, add `"apps.summarisation"` after `"apps.copilot"` in `INSTALLED_APPS`.

- [ ] **Step 5: Generate and check migration**

```bash
cd backend
python manage.py makemigrations summarisation
python manage.py check
```

Expected: Migration `0001_initial.py` generated, system check passes.

- [ ] **Step 6: Commit**

```bash
git add backend/apps/summarisation/ backend/apps/copilot/models.py backend/sis_backend/settings.py
git commit -m "feat(summarisation): scaffold app with SummarisationRequest model and AIAuditAction entries"
```

---

## Task 2: Provider and prompt layer

**Files:**
- Create: `backend/apps/summarisation/prompts.py`
- Create: `backend/apps/summarisation/providers.py`

- [ ] **Step 1: Create the structured extraction prompt**

Create `backend/apps/summarisation/prompts.py`:
```python
SUMMARISATION_SYSTEM_PROMPT = """You are an academic advising assistant at a university.

Extract a structured summary from the following raw advising notes.

Return ONLY valid JSON with exactly these three fields:
- "key_issues": array of 1-5 concise issue descriptions found in the notes
- "recommended_actions": array of 1-5 specific next steps based on what was discussed
- "urgency_level": exactly one of "Routine", "Follow-up Needed", or "Urgent"

Rules:
- Do not invent information not present in the input.
- Do not include student names, IDs, or identifying information in the output.
- Do not include personal opinions or diagnoses.
- Keep each issue and action to one sentence.
"""


MAX_INPUT_LENGTH = 5000
```

- [ ] **Step 2: Create the provider layer**

Create `backend/apps/summarisation/providers.py`:
```python
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

import requests
from django.conf import settings

from .prompts import SUMMARISATION_SYSTEM_PROMPT


@dataclass(frozen=True)
class SummarisationResult:
    key_issues: list[str]
    recommended_actions: list[str]
    urgency_level: str
    provider: str
    model_name: str
    latency_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


VALID_URGENCY_LEVELS = {"Routine", "Follow-up Needed", "Urgent"}


def _parse_structured_output(raw: str) -> dict[str, Any]:
    cleaned = raw.strip()
    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)
    parsed = json.loads(cleaned)
    if not isinstance(parsed.get("key_issues"), list):
        parsed["key_issues"] = []
    if not isinstance(parsed.get("recommended_actions"), list):
        parsed["recommended_actions"] = []
    urgency = parsed.get("urgency_level", "Routine")
    if urgency not in VALID_URGENCY_LEVELS:
        urgency = "Routine"
    parsed["urgency_level"] = urgency
    parsed["key_issues"] = [str(item) for item in parsed["key_issues"][:5]]
    parsed["recommended_actions"] = [str(item) for item in parsed["recommended_actions"][:5]]
    return parsed


class DeterministicSummarisationProvider:
    provider = "deterministic"
    model_name = "deterministic-summarisation-v1"

    def summarise(self, raw_text: str) -> SummarisationResult:
        sentences = [s.strip() for s in raw_text.replace("\n", ". ").split(".") if s.strip()]
        key_issues = sentences[:3] if sentences else ["No issues identified from input."]
        recommended_actions = ["Review notes with student.", "Schedule follow-up meeting."]
        urgency = "Routine"
        lower = raw_text.lower()
        if any(word in lower for word in ("urgent", "crisis", "emergency", "immediate")):
            urgency = "Urgent"
        elif any(word in lower for word in ("follow-up", "follow up", "concern", "struggling")):
            urgency = "Follow-up Needed"
        return SummarisationResult(
            key_issues=key_issues,
            recommended_actions=recommended_actions,
            urgency_level=urgency,
            provider=self.provider,
            model_name=self.model_name,
        )


class OpenAISummarisationProvider:
    provider = "openai_compatible"

    def __init__(self):
        api_key = getattr(settings, "OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai_compatible.")
        self.api_key = api_key
        self.base_url = getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
        self.model_name = getattr(settings, "OPENAI_MODEL", "").strip() or "gpt-4o-mini"
        self.timeout = int(getattr(settings, "AI_REQUEST_TIMEOUT_SECONDS", 20))

    def summarise(self, raw_text: str) -> SummarisationResult:
        started = time.monotonic()
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": SUMMARISATION_SYSTEM_PROMPT},
                    {"role": "user", "content": raw_text},
                ],
                "temperature": 0.1,
            },
            timeout=self.timeout,
        )
        latency_ms = int((time.monotonic() - started) * 1000)
        if response.status_code >= 400:
            raise RuntimeError(f"Summarisation provider failed with status {response.status_code}.")
        payload = response.json()
        raw_content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = _parse_structured_output(raw_content)
        return SummarisationResult(
            key_issues=parsed["key_issues"],
            recommended_actions=parsed["recommended_actions"],
            urgency_level=parsed["urgency_level"],
            provider=self.provider,
            model_name=self.model_name,
            latency_ms=latency_ms,
            metadata={"finishReason": payload.get("choices", [{}])[0].get("finish_reason", "")},
        )


def get_summarisation_provider():
    provider = getattr(settings, "AI_PROVIDER", "deterministic").strip() or "deterministic"
    if provider == "deterministic":
        return DeterministicSummarisationProvider()
    if provider == "openai_compatible":
        return OpenAISummarisationProvider()
    raise ValueError(f"Unsupported AI_PROVIDER for summarisation: {provider}")
```

- [ ] **Step 3: Run basic import check**

```bash
cd backend
python -c "from apps.summarisation.providers import get_summarisation_provider; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add backend/apps/summarisation/prompts.py backend/apps/summarisation/providers.py
git commit -m "feat(summarisation): add provider layer with deterministic and OpenAI-compatible providers"
```

---

## Task 3: Service layer and audit integration

**Files:**
- Create: `backend/apps/summarisation/services.py`

- [ ] **Step 1: Create the service layer**

Create `backend/apps/summarisation/services.py`:
```python
from __future__ import annotations

import json
import time
from typing import Any

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.audit.models import AuditCategory, AuditSeverity
from apps.audit.services import record_audit_event_safely
from apps.copilot.audit import record_ai_audit
from apps.copilot.models import AIAuditAction, CopilotConfidence, CopilotProvider
from apps.copilot.safety import redact_metadata, redact_text
from apps.students.models import AdvisingNote, AdvisingNoteStatus

from .models import SummarisationRequest, SummarisationStatus
from .prompts import MAX_INPUT_LENGTH
from .providers import SummarisationResult, get_summarisation_provider


def validate_input_text(text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        raise serializers.ValidationError({"raw_text": "Input text is required."})
    if len(cleaned) > MAX_INPUT_LENGTH:
        raise serializers.ValidationError(
            {"raw_text": f"Input must be {MAX_INPUT_LENGTH} characters or fewer. Current: {len(cleaned)}."}
        )
    return cleaned


@transaction.atomic
def create_summarisation_request(
    *,
    user,
    raw_text: str,
    student=None,
    request=None,
) -> SummarisationRequest:
    cleaned = validate_input_text(raw_text)
    started = time.monotonic()

    try:
        provider = get_summarisation_provider()
        result: SummarisationResult = provider.summarise(cleaned)
    except Exception as exc:
        record_ai_audit(
            action=AIAuditAction.SUMMARISATION_REQUEST,
            user=user,
            student=student,
            input_text=cleaned,
            output_text=f"Provider error: {str(exc)[:500]}",
            provider=CopilotProvider.SYSTEM,
            model_name="provider-error",
            metadata={"error": True},
        )
        raise serializers.ValidationError({"detail": "Summarisation service is temporarily unavailable."}) from exc

    latency_ms = result.latency_ms or int((time.monotonic() - started) * 1000)
    ai_output = {
        "key_issues": result.key_issues,
        "recommended_actions": result.recommended_actions,
        "urgency_level": result.urgency_level,
    }

    summarisation = SummarisationRequest.objects.create(
        user=user,
        student=student,
        raw_input_text=cleaned,
        ai_output=ai_output,
        status=SummarisationStatus.PENDING,
        provider=result.provider,
        model_name=result.model_name,
        latency_ms=latency_ms,
    )

    record_ai_audit(
        action=AIAuditAction.SUMMARISATION_REQUEST,
        user=user,
        student=student,
        input_text=cleaned,
        output_text=json.dumps(ai_output),
        provider=result.provider,
        model_name=result.model_name,
        metadata={
            "summarisationId": str(summarisation.id),
            "latencyMs": latency_ms,
            **redact_metadata(result.metadata),
        },
    )
    record_audit_event_safely(
        actor=user,
        category=AuditCategory.AI,
        action="SUMMARISATION_REQUEST",
        summary="Staff summarisation request processed.",
        target_type="SummarisationRequest",
        target_id=str(summarisation.id),
        severity=AuditSeverity.INFO,
        metadata={
            "summarisationId": str(summarisation.id),
            "provider": result.provider,
            "studentId": str(student.id) if student else None,
        },
        request=request,
    )
    return summarisation


@transaction.atomic
def approve_summarisation(
    *,
    user,
    summarisation: SummarisationRequest,
    human_edited_output: dict[str, Any],
    request=None,
) -> SummarisationRequest:
    if summarisation.status != SummarisationStatus.PENDING:
        raise serializers.ValidationError({"detail": "This summarisation has already been processed."})

    summarisation.human_edited_output = human_edited_output
    summarisation.status = SummarisationStatus.APPROVED
    summarisation.approved_at = timezone.now()

    if summarisation.student:
        note_text = _format_note_text(human_edited_output)
        note = AdvisingNote.objects.create(
            student=summarisation.student,
            created_by_user=user,
            note_text=note_text,
            status=AdvisingNoteStatus.APPROVED,
            approved_by_user=user,
            approved_at=timezone.now(),
        )
        summarisation.advising_note = note

    summarisation.save()

    record_ai_audit(
        action=AIAuditAction.SUMMARISATION_APPROVED,
        user=user,
        student=summarisation.student,
        input_text=summarisation.raw_input_text,
        output_text=json.dumps(summarisation.ai_output),
        provider=summarisation.provider,
        model_name=summarisation.model_name,
        approved_by=user,
        metadata={
            "summarisationId": str(summarisation.id),
            "humanEditedOutput": human_edited_output,
            "advisingNoteId": str(summarisation.advising_note_id) if summarisation.advising_note_id else None,
        },
    )
    record_audit_event_safely(
        actor=user,
        category=AuditCategory.AI,
        action="SUMMARISATION_APPROVED",
        summary="Staff summarisation approved and saved as official record.",
        target_type="SummarisationRequest",
        target_id=str(summarisation.id),
        severity=AuditSeverity.INFO,
        metadata={
            "summarisationId": str(summarisation.id),
            "advisingNoteId": str(summarisation.advising_note_id) if summarisation.advising_note_id else None,
            "studentId": str(summarisation.student_id) if summarisation.student_id else None,
        },
        request=request,
    )
    return summarisation


def _format_note_text(output: dict[str, Any]) -> str:
    lines = []
    urgency = output.get("urgency_level", "Routine")
    lines.append(f"Urgency: {urgency}")
    lines.append("")
    lines.append("Key Issues:")
    for issue in output.get("key_issues", []):
        lines.append(f"- {issue}")
    lines.append("")
    lines.append("Recommended Actions:")
    for action in output.get("recommended_actions", []):
        lines.append(f"- {action}")
    return "\n".join(lines)
```

- [ ] **Step 2: Verify import**

```bash
cd backend
python -c "from apps.summarisation.services import create_summarisation_request; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/apps/summarisation/services.py
git commit -m "feat(summarisation): add service layer with audit logging and advising note creation"
```

---

## Task 4: Serializers, views, and URL wiring

**Files:**
- Create: `backend/apps/summarisation/serializers.py`
- Create: `backend/apps/summarisation/views.py`
- Create: `backend/apps/summarisation/urls.py`
- Modify: `backend/sis_backend/urls.py:35`
- Modify: `backend/apps/accounts/access.py`

- [ ] **Step 1: Create serializers**

Create `backend/apps/summarisation/serializers.py`:
```python
from rest_framework import serializers

from .models import SummarisationRequest, UrgencyLevel
from .prompts import MAX_INPUT_LENGTH


class SummariseInputSerializer(serializers.Serializer):
    raw_text = serializers.CharField(max_length=MAX_INPUT_LENGTH)
    student_id = serializers.UUIDField(required=False, allow_null=True)


class SummarisationOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SummarisationRequest
        fields = [
            "id",
            "raw_input_text",
            "ai_output",
            "human_edited_output",
            "status",
            "provider",
            "model_name",
            "latency_ms",
            "student",
            "advising_note",
            "created_at",
            "approved_at",
        ]
        read_only_fields = fields


class SummariseApproveInputSerializer(serializers.Serializer):
    key_issues = serializers.ListField(child=serializers.CharField(max_length=500), max_length=5)
    recommended_actions = serializers.ListField(child=serializers.CharField(max_length=500), max_length=5)
    urgency_level = serializers.ChoiceField(choices=UrgencyLevel.choices)
```

- [ ] **Step 2: Create views**

Create `backend/apps/summarisation/views.py`:
```python
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
```

- [ ] **Step 3: Create URL patterns**

Create `backend/apps/summarisation/urls.py`:
```python
from django.urls import path

from .views import SummariseApproveView, SummariseView

urlpatterns = [
    path("ai/summarise/", SummariseView.as_view(), name="summarise-request"),
    path("ai/summarise/<uuid:summarisation_id>/approve/", SummariseApproveView.as_view(), name="summarise-approve"),
]
```

- [ ] **Step 4: Wire URLs into root**

In `backend/sis_backend/urls.py`, add after the copilot line:
```python
    path("api/v1/", include("apps.summarisation.urls")),
```

- [ ] **Step 5: Add access policies**

In `backend/apps/accounts/access.py`, add to `PROTECTED_API_ROUTE_POLICIES` after the `copilot-message-feedback` entry:
```python
        "summarise-request": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
        "summarise-approve": AccessPolicy(
            allowed_roles=frozenset({RoleCode.ADVISOR, RoleCode.ADMIN})
        ),
```

- [ ] **Step 6: Run system check**

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
```

Expected: System check passes, no new migrations needed.

- [ ] **Step 7: Commit**

```bash
git add backend/apps/summarisation/serializers.py backend/apps/summarisation/views.py backend/apps/summarisation/urls.py backend/sis_backend/urls.py backend/apps/accounts/access.py
git commit -m "feat(summarisation): add API endpoints with access policy enforcement"
```

---

## Task 5: Backend tests

**Files:**
- Create: `backend/apps/summarisation/tests/test_services.py`
- Create: `backend/apps/summarisation/tests/test_api.py`

- [ ] **Step 1: Write service layer tests**

Create `backend/apps/summarisation/tests/test_services.py`:
```python
import pytest
from django.test import override_settings

from apps.copilot.models import AIAuditLog, AIAuditAction
from apps.students.models import AdvisingNote, AdvisingNoteStatus
from apps.summarisation.models import SummarisationRequest, SummarisationStatus
from apps.summarisation.services import create_summarisation_request, approve_summarisation, validate_input_text


@pytest.fixture
def advisor_user(db):
    from apps.accounts.models import User, Role
    from apps.accounts.constants import RoleCode
    role, _ = Role.objects.get_or_create(code=RoleCode.ADVISOR, defaults={"name": "Advisor"})
    user = User.objects.create_user(username="advisor.test", password="TestPass123!", primary_role=RoleCode.ADVISOR)
    return user


@pytest.fixture
def student_profile(db, advisor_user):
    from apps.students.models import StudentProfile
    from apps.accounts.models import User, Role
    from apps.accounts.constants import RoleCode
    role, _ = Role.objects.get_or_create(code=RoleCode.STUDENT, defaults={"name": "Student"})
    student_user = User.objects.create_user(
        username="student.sumtest", password="TestPass123!", primary_role=RoleCode.STUDENT
    )
    return StudentProfile.objects.create(
        user=student_user,
        student_number="SUM001",
        full_name="Test Student for Summarisation",
        date_of_birth="2000-01-01",
        gender="M",
        programme="BSc Computer Science",
        year_of_study=2,
        contact_email="sumtest@example.com",
    )


@pytest.mark.django_db
@override_settings(AI_PROVIDER="deterministic")
def test_create_summarisation_request_deterministic(advisor_user):
    result = create_summarisation_request(
        user=advisor_user,
        raw_text="Student is struggling with calculus and has missed three classes. Need to discuss study plan.",
    )
    assert result.status == SummarisationStatus.PENDING
    assert result.provider == "deterministic"
    assert "key_issues" in result.ai_output
    assert "recommended_actions" in result.ai_output
    assert result.ai_output["urgency_level"] in {"Routine", "Follow-up Needed", "Urgent"}
    audit = AIAuditLog.objects.filter(action=AIAuditAction.SUMMARISATION_REQUEST).first()
    assert audit is not None
    assert audit.user == advisor_user


@pytest.mark.django_db
@override_settings(AI_PROVIDER="deterministic")
def test_create_summarisation_request_with_student(advisor_user, student_profile):
    result = create_summarisation_request(
        user=advisor_user,
        raw_text="Student wants to drop a course past the deadline. Financial aid implications discussed.",
        student=student_profile,
    )
    assert result.student == student_profile


@pytest.mark.django_db
@override_settings(AI_PROVIDER="deterministic")
def test_approve_summarisation_creates_advising_note(advisor_user, student_profile):
    summarisation = create_summarisation_request(
        user=advisor_user,
        raw_text="Discussed graduate school preparation and recommendation letters.",
        student=student_profile,
    )
    approved = approve_summarisation(
        user=advisor_user,
        summarisation=summarisation,
        human_edited_output={
            "key_issues": ["Needs recommendation letter for grad school"],
            "recommended_actions": ["Connect with research supervisor"],
            "urgency_level": "Routine",
        },
    )
    assert approved.status == SummarisationStatus.APPROVED
    assert approved.advising_note is not None
    note = approved.advising_note
    assert note.status == AdvisingNoteStatus.APPROVED
    assert note.student == student_profile
    assert "recommendation letter" in note.note_text
    audit = AIAuditLog.objects.filter(action=AIAuditAction.SUMMARISATION_APPROVED).first()
    assert audit is not None
    assert audit.approved_by == advisor_user


@pytest.mark.django_db
@override_settings(AI_PROVIDER="deterministic")
def test_approve_without_student_no_advising_note(advisor_user):
    summarisation = create_summarisation_request(
        user=advisor_user,
        raw_text="General helpdesk ticket about system access.",
    )
    approved = approve_summarisation(
        user=advisor_user,
        summarisation=summarisation,
        human_edited_output={
            "key_issues": ["System access request"],
            "recommended_actions": ["Reset credentials"],
            "urgency_level": "Routine",
        },
    )
    assert approved.status == SummarisationStatus.APPROVED
    assert approved.advising_note is None


@pytest.mark.django_db
def test_validate_input_text_empty():
    with pytest.raises(Exception):
        validate_input_text("")


@pytest.mark.django_db
def test_validate_input_text_too_long():
    with pytest.raises(Exception):
        validate_input_text("x" * 5001)


@pytest.mark.django_db
@override_settings(AI_PROVIDER="deterministic")
def test_urgent_detection(advisor_user):
    result = create_summarisation_request(
        user=advisor_user,
        raw_text="Urgent: student has a family emergency and needs immediate extension on all deadlines.",
    )
    assert result.ai_output["urgency_level"] == "Urgent"
```

- [ ] **Step 2: Write API permission tests**

Create `backend/apps/summarisation/tests/test_api.py`:
```python
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, Role
from apps.accounts.constants import RoleCode
from apps.students.models import StudentProfile
from apps.summarisation.models import SummarisationRequest


@pytest.fixture
def roles(db):
    for code in RoleCode.values:
        Role.objects.get_or_create(code=code, defaults={"name": code.title()})


@pytest.fixture
def advisor_client(roles):
    user = User.objects.create_user(username="advisor.api", password="TestPass123!", primary_role=RoleCode.ADVISOR)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def admin_client(roles):
    user = User.objects.create_user(username="admin.api", password="TestPass123!", primary_role=RoleCode.ADMIN)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def student_client(roles):
    user = User.objects.create_user(username="student.api", password="TestPass123!", primary_role=RoleCode.STUDENT)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def faculty_client(roles):
    user = User.objects.create_user(username="faculty.api", password="TestPass123!", primary_role=RoleCode.FACULTY)
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
class TestSummariseEndpointAccess:
    def test_advisor_can_summarise(self, advisor_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = advisor_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Student missed three classes."})
        assert response.status_code == 201
        assert "ai_output" in response.data

    def test_admin_can_summarise(self, admin_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = admin_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Helpdesk ticket about password reset."})
        assert response.status_code == 201

    def test_student_denied(self, student_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = student_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Some text."})
        assert response.status_code == 403

    def test_faculty_denied(self, faculty_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = faculty_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Some text."})
        assert response.status_code == 403

    def test_empty_text_rejected(self, advisor_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = advisor_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": ""})
        assert response.status_code == 400

    def test_text_too_long_rejected(self, advisor_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = advisor_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "x" * 5001})
        assert response.status_code == 400


@pytest.mark.django_db
class TestSummariseApproveEndpoint:
    def test_approve_with_student_creates_note(self, advisor_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, user = advisor_client
        student_user = User.objects.create_user(
            username="student.approve", password="TestPass123!", primary_role=RoleCode.STUDENT
        )
        student = StudentProfile.objects.create(
            user=student_user,
            student_number="APR001",
            full_name="Approve Test Student",
            date_of_birth="2000-01-01",
            gender="F",
            programme="BSc IT",
            year_of_study=1,
            contact_email="approve@example.com",
        )
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Meeting about course load.", "student_id": str(student.id)})
        assert response.status_code == 201
        summarisation_id = response.data["id"]
        approve_response = client.post(
            f"/api/v1/ai/summarise/{summarisation_id}/approve/",
            {
                "key_issues": ["Course load too heavy"],
                "recommended_actions": ["Drop one elective"],
                "urgency_level": "Follow-up Needed",
            },
            format="json",
        )
        assert approve_response.status_code == 200
        assert approve_response.data["status"] == "APPROVED"
        assert approve_response.data["advising_note"] is not None

    def test_approve_without_student_no_note(self, admin_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, user = admin_client
        response = client.post("/api/v1/ai/summarise/", {"raw_text": "Admin helpdesk ticket."})
        summarisation_id = response.data["id"]
        approve_response = client.post(
            f"/api/v1/ai/summarise/{summarisation_id}/approve/",
            {
                "key_issues": ["Access issue"],
                "recommended_actions": ["Reset account"],
                "urgency_level": "Routine",
            },
            format="json",
        )
        assert approve_response.status_code == 200
        assert approve_response.data["advising_note"] is None

    def test_student_cannot_approve(self, student_client, settings):
        settings.AI_PROVIDER = "deterministic"
        client, _ = student_client
        import uuid
        response = client.post(f"/api/v1/ai/summarise/{uuid.uuid4()}/approve/", {}, format="json")
        assert response.status_code == 403
```

- [ ] **Step 3: Run tests**

```bash
cd backend
pytest apps/summarisation/tests/ -v
```

Expected: All tests pass.

- [ ] **Step 4: Run full check and lint**

```bash
cd backend
python manage.py check
ruff check apps/summarisation/
```

Expected: No errors.

- [ ] **Step 5: Commit**

```bash
git add backend/apps/summarisation/tests/
git commit -m "test(summarisation): add service and API permission tests"
```

---

## Task 6: Demo seed command

**Files:**
- Create: `backend/apps/summarisation/management/commands/seed_summarisation_demo.py`

- [ ] **Step 1: Create the seed command**

Create `backend/apps/summarisation/management/commands/seed_summarisation_demo.py`:
```python
from django.core.management.base import BaseCommand

from apps.accounts.constants import RoleCode
from apps.accounts.models import Role, User
from apps.students.models import StudentProfile
from apps.summarisation.services import approve_summarisation, create_summarisation_request


DEMO_SCENARIOS = [
    {
        "title": "Academic probation meeting",
        "raw_text": (
            "Met with student regarding poor performance this semester. "
            "Currently on academic probation after failing two core courses last term. "
            "Student reports difficulty concentrating due to part-time job taking too many hours. "
            "Discussed reducing work hours and using campus tutoring services. "
            "Student agreed to attend at least two tutoring sessions per week and will "
            "submit a revised study schedule by next Friday."
        ),
        "approve": True,
        "edited_output": {
            "key_issues": [
                "Academic probation after failing two core courses",
                "Part-time job hours interfering with study time",
                "Difficulty concentrating reported by student",
            ],
            "recommended_actions": [
                "Reduce work hours to maximum 10 per week",
                "Attend campus tutoring at least twice weekly",
                "Submit revised study schedule by next Friday",
            ],
            "urgency_level": "Follow-up Needed",
        },
    },
    {
        "title": "Course withdrawal discussion",
        "raw_text": (
            "Student requesting to withdraw from MATH201 past the official deadline. "
            "Reason: family emergency requiring travel for three weeks during mid-semester. "
            "Student has documentation from hospital confirming family member illness. "
            "Financial aid office confirmed no impact on scholarship if approved as extenuating circumstances. "
            "Recommended filing the late withdrawal form with supporting documents by end of this week."
        ),
        "approve": True,
        "edited_output": {
            "key_issues": [
                "Late withdrawal request for MATH201 past deadline",
                "Family emergency with hospital documentation",
                "Financial aid confirmed no scholarship impact",
            ],
            "recommended_actions": [
                "File late withdrawal form with supporting documents",
                "Submit by end of this week",
                "Follow up with financial aid office for confirmation letter",
            ],
            "urgency_level": "Urgent",
        },
    },
    {
        "title": "Graduate school preparation",
        "raw_text": (
            "Third-year student interested in applying to MSc programmes in data science. "
            "GPA currently 3.4, needs to maintain above 3.2 for target programmes. "
            "Discussed research opportunities with Dr. Smith in the ML lab. "
            "Student needs two recommendation letters, currently has one confirmed. "
            "Advised to join the undergraduate research programme next semester and "
            "start drafting personal statement over the summer break."
        ),
        "approve": False,
        "edited_output": None,
    },
    {
        "title": "Personal circumstances extension",
        "raw_text": (
            "Student requesting two-week extension on all assignments due to death in immediate family. "
            "Student has been absent for one week already. Bereavement policy allows up to "
            "two weeks of compassionate leave with documentation. Student provided death certificate. "
            "Contacted all three course lecturers who confirmed extensions are acceptable. "
            "Student will return to campus next Monday and submit revised completion dates."
        ),
        "approve": True,
        "edited_output": {
            "key_issues": [
                "Bereavement leave request following death in immediate family",
                "One week absence already taken",
                "All course lecturers confirmed extension acceptable",
            ],
            "recommended_actions": [
                "Approve two-week compassionate leave per bereavement policy",
                "Record documentation on file",
                "Student to submit revised completion dates upon return Monday",
            ],
            "urgency_level": "Urgent",
        },
    },
    {
        "title": "Internship credit approval",
        "raw_text": (
            "Student seeking academic credit for summer internship at TechCorp Ltd. "
            "Role is software development, 12 weeks full-time. Supervisor confirmed "
            "willingness to complete evaluation form. Checked programme requirements: "
            "internship credit available under COSC490 if minimum 300 hours and relevant to degree. "
            "Student needs to submit placement agreement form and learning objectives "
            "before internship start date of June 1."
        ),
        "approve": False,
        "edited_output": None,
    },
]


class Command(BaseCommand):
    help = "Seed demonstration summarisation requests with real-world advising scenarios."

    def handle(self, *args, **options):
        Role.objects.get_or_create(code=RoleCode.ADVISOR, defaults={"name": "Advisor"})
        Role.objects.get_or_create(code=RoleCode.STUDENT, defaults={"name": "Student"})

        advisor, _ = User.objects.get_or_create(
            username="advisor.demo1",
            defaults={"primary_role": RoleCode.ADVISOR, "first_name": "Demo", "last_name": "Advisor"},
        )
        if not advisor.has_usable_password():
            advisor.set_password("DemoPass123!")
            advisor.save()

        student_user, _ = User.objects.get_or_create(
            username="student.demo1",
            defaults={"primary_role": RoleCode.STUDENT, "first_name": "Demo", "last_name": "Student"},
        )
        if not student_user.has_usable_password():
            student_user.set_password("DemoPass123!")
            student_user.save()

        student, _ = StudentProfile.objects.get_or_create(
            user=student_user,
            defaults={
                "student_number": "STU001",
                "full_name": "Demo Student",
                "date_of_birth": "2001-05-15",
                "gender": "M",
                "programme": "BSc Computer Science",
                "year_of_study": 3,
                "contact_email": "student.demo1@example.com",
            },
        )

        created_count = 0
        approved_count = 0

        for scenario in DEMO_SCENARIOS:
            existing = SummarisationRequest.objects.filter(
                user=advisor, raw_input_text=scenario["raw_text"][:100]
            ).first()
            if existing:
                self.stdout.write(f"  Skipping existing: {scenario['title']}")
                continue

            from django.conf import settings
            original_provider = settings.AI_PROVIDER
            settings.AI_PROVIDER = "deterministic"

            summarisation = create_summarisation_request(
                user=advisor,
                raw_text=scenario["raw_text"],
                student=student,
            )
            created_count += 1
            self.stdout.write(f"  Created: {scenario['title']}")

            if scenario["approve"] and scenario["edited_output"]:
                approve_summarisation(
                    user=advisor,
                    summarisation=summarisation,
                    human_edited_output=scenario["edited_output"],
                )
                approved_count += 1
                self.stdout.write(f"  Approved: {scenario['title']}")

            settings.AI_PROVIDER = original_provider

        self.stdout.write(self.style.SUCCESS(
            f"Summarisation demo seeded: {created_count} created, {approved_count} approved."
        ))
```

- [ ] **Step 2: Run the seed command**

```bash
cd backend
python manage.py migrate
python manage.py seed_summarisation_demo
```

Expected: Output showing 5 scenarios created, 3 approved.

- [ ] **Step 3: Commit**

```bash
git add backend/apps/summarisation/management/
git commit -m "feat(summarisation): add demo seed command with 5 real-world advising scenarios"
```

---

## Task 7: Frontend hook and shared components

**Files:**
- Create: `frontend/src/hooks/useSummarisation.ts`
- Create: `frontend/src/features/summarisation/SummarisationForm.tsx`
- Create: `frontend/src/features/summarisation/SummarisationResult.tsx`

- [ ] **Step 1: Create the frontend hook**

Create `frontend/src/hooks/useSummarisation.ts`:
```typescript
import { useMutation } from '@tanstack/react-query'

import { api } from '@/lib/api'

interface SummariseInput {
  raw_text: string
  student_id?: string | null
}

interface SummarisationOutput {
  id: string
  raw_input_text: string
  ai_output: {
    key_issues: string[]
    recommended_actions: string[]
    urgency_level: 'Routine' | 'Follow-up Needed' | 'Urgent'
  }
  human_edited_output: {
    key_issues: string[]
    recommended_actions: string[]
    urgency_level: string
  } | null
  status: 'PENDING' | 'APPROVED' | 'DISCARDED'
  provider: string
  model_name: string
  latency_ms: number | null
  student: string | null
  advising_note: string | null
  created_at: string
  approved_at: string | null
}

interface ApproveInput {
  key_issues: string[]
  recommended_actions: string[]
  urgency_level: string
}

export function useSummariseMutation() {
  return useMutation({
    mutationFn: async (input: SummariseInput): Promise<SummarisationOutput> => {
      const response = await api.post('/ai/summarise/', input)
      return response.data
    },
  })
}

export function useApproveSummarisationMutation(summarisationId: string) {
  return useMutation({
    mutationFn: async (input: ApproveInput): Promise<SummarisationOutput> => {
      const response = await api.post(`/ai/summarise/${summarisationId}/approve/`, input)
      return response.data
    },
  })
}
```

- [ ] **Step 2: Create the input form component**

Create directory and file:
```bash
mkdir -p frontend/src/features/summarisation
```

Create `frontend/src/features/summarisation/SummarisationForm.tsx`:
```tsx
import { useState } from 'react'

import { Button } from '@/components/ui/Button'
import { Textarea } from '@/components/ui/Textarea'

const MAX_INPUT_LENGTH = 5000
const GOVERNANCE_NOTICE =
  'AI-generated summaries must be reviewed and approved before saving. The saved record will reflect your approved version, not the raw AI output.'

export function SummarisationForm({
  onSubmit,
  isPending,
}: {
  onSubmit: (rawText: string) => void
  isPending: boolean
}) {
  const [text, setText] = useState('')
  const charCount = text.length
  const isOverLimit = charCount > MAX_INPUT_LENGTH
  const isEmpty = text.trim().length === 0

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        {GOVERNANCE_NOTICE}
      </div>
      <div>
        <Textarea
          id="summarise-input"
          label="Raw advising notes"
          rows={8}
          placeholder="Paste or type your advising notes, meeting minutes, or helpdesk ticket here."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={isPending}
        />
        <div className="mt-1 flex justify-end">
          <span
            className={`text-xs ${isOverLimit ? 'font-medium text-red-600' : 'text-neutral-500'}`}
          >
            {charCount} / {MAX_INPUT_LENGTH}
          </span>
        </div>
        {isOverLimit && (
          <p className="mt-1 text-sm text-red-600">
            Input exceeds the {MAX_INPUT_LENGTH} character limit. Please shorten your text.
          </p>
        )}
      </div>
      <Button
        onClick={() => onSubmit(text)}
        loading={isPending}
        disabled={isEmpty || isOverLimit || isPending}
      >
        Generate summary
      </Button>
    </div>
  )
}
```

- [ ] **Step 3: Create the editable result component**

Create `frontend/src/features/summarisation/SummarisationResult.tsx`:
```tsx
import { useState } from 'react'

import { Button } from '@/components/ui/Button'

interface SummarisationResultProps {
  keyIssues: string[]
  recommendedActions: string[]
  urgencyLevel: string
  onApprove: (output: { key_issues: string[]; recommended_actions: string[]; urgency_level: string }) => void
  onDiscard: () => void
  isApproving: boolean
}

export function SummarisationResult({
  keyIssues,
  recommendedActions,
  urgencyLevel,
  onApprove,
  onDiscard,
  isApproving,
}: SummarisationResultProps) {
  const [issues, setIssues] = useState<string[]>(keyIssues)
  const [actions, setActions] = useState<string[]>(recommendedActions)
  const [urgency, setUrgency] = useState(urgencyLevel)

  const updateItem = (
    list: string[],
    setList: (value: string[]) => void,
    index: number,
    value: string,
  ) => {
    const updated = [...list]
    updated[index] = value
    setList(updated)
  }

  const removeItem = (list: string[], setList: (value: string[]) => void, index: number) => {
    setList(list.filter((_, i) => i !== index))
  }

  const addItem = (list: string[], setList: (value: string[]) => void) => {
    if (list.length < 5) {
      setList([...list, ''])
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <label className="text-sm font-medium text-neutral-700">Urgency level</label>
        <select
          className="mt-1 block w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          value={urgency}
          onChange={(e) => setUrgency(e.target.value)}
          disabled={isApproving}
        >
          <option value="Routine">Routine</option>
          <option value="Follow-up Needed">Follow-up Needed</option>
          <option value="Urgent">Urgent</option>
        </select>
      </div>

      <EditableList
        label="Key issues"
        items={issues}
        onUpdate={(index, value) => updateItem(issues, setIssues, index, value)}
        onRemove={(index) => removeItem(issues, setIssues, index)}
        onAdd={() => addItem(issues, setIssues)}
        disabled={isApproving}
      />

      <EditableList
        label="Recommended actions"
        items={actions}
        onUpdate={(index, value) => updateItem(actions, setActions, index, value)}
        onRemove={(index) => removeItem(actions, setActions, index)}
        onAdd={() => addItem(actions, setActions)}
        disabled={isApproving}
      />

      <div className="flex gap-3">
        <Button
          onClick={() =>
            onApprove({ key_issues: issues.filter(Boolean), recommended_actions: actions.filter(Boolean), urgency_level: urgency })
          }
          loading={isApproving}
          disabled={isApproving || issues.filter(Boolean).length === 0}
        >
          Approve and save
        </Button>
        <Button variant="secondary" onClick={onDiscard} disabled={isApproving}>
          Discard
        </Button>
      </div>
    </div>
  )
}

function EditableList({
  label,
  items,
  onUpdate,
  onRemove,
  onAdd,
  disabled,
}: {
  label: string
  items: string[]
  onUpdate: (index: number, value: string) => void
  onRemove: (index: number) => void
  onAdd: () => void
  disabled: boolean
}) {
  return (
    <div>
      <label className="text-sm font-medium text-neutral-700">{label}</label>
      <div className="mt-2 space-y-2">
        {items.map((item, index) => (
          <div key={index} className="flex gap-2">
            <input
              type="text"
              className="flex-1 rounded-lg border border-neutral-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              value={item}
              onChange={(e) => onUpdate(index, e.target.value)}
              disabled={disabled}
            />
            <button
              type="button"
              className="rounded-lg border border-neutral-300 px-2 py-1 text-sm text-neutral-500 hover:bg-neutral-100 disabled:opacity-50"
              onClick={() => onRemove(index)}
              disabled={disabled}
            >
              Remove
            </button>
          </div>
        ))}
      </div>
      {items.length < 5 && (
        <button
          type="button"
          className="mt-2 text-sm text-primary hover:underline disabled:opacity-50"
          onClick={onAdd}
          disabled={disabled}
        >
          + Add item
        </button>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Run typecheck**

```bash
cd frontend
npm run typecheck
```

Expected: No type errors.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/hooks/useSummarisation.ts frontend/src/features/summarisation/
git commit -m "feat(summarisation): add frontend hook and reusable form/result components"
```

---

## Task 8: Replace placeholder AISummarisationPanel

**Files:**
- Modify: `frontend/src/components/advisor/AISummarisationPanel.tsx`

- [ ] **Step 1: Replace the disabled placeholder with live component**

Rewrite `frontend/src/components/advisor/AISummarisationPanel.tsx`:
```tsx
import { useState } from 'react'

import { SummarisationForm } from '@/features/summarisation/SummarisationForm'
import { SummarisationResult } from '@/features/summarisation/SummarisationResult'
import { useApproveSummarisationMutation, useSummariseMutation } from '@/hooks/useSummarisation'

export function AISummarisationPanel({ studentId }: { studentId?: string }) {
  const summarise = useSummariseMutation()
  const [summarisationId, setSummarisationId] = useState<string | null>(null)
  const approve = useApproveSummarisationMutation(summarisationId ?? '')
  const [success, setSuccess] = useState(false)

  const handleSubmit = (rawText: string) => {
    setSuccess(false)
    summarise.mutate(
      { raw_text: rawText, student_id: studentId ?? null },
      { onSuccess: (data) => setSummarisationId(data.id) },
    )
  }

  const handleApprove = (output: {
    key_issues: string[]
    recommended_actions: string[]
    urgency_level: string
  }) => {
    approve.mutate(output, {
      onSuccess: () => {
        setSuccess(true)
        setSummarisationId(null)
        summarise.reset()
      },
    })
  }

  const handleDiscard = () => {
    setSummarisationId(null)
    summarise.reset()
  }

  if (success) {
    return (
      <div className="space-y-4">
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
          Summary approved and saved as an official advising note.
        </div>
        <button
          type="button"
          className="text-sm text-primary hover:underline"
          onClick={() => setSuccess(false)}
        >
          Summarise another note
        </button>
      </div>
    )
  }

  if (summarise.data && summarisationId) {
    return (
      <SummarisationResult
        keyIssues={summarise.data.ai_output.key_issues}
        recommendedActions={summarise.data.ai_output.recommended_actions}
        urgencyLevel={summarise.data.ai_output.urgency_level}
        onApprove={handleApprove}
        onDiscard={handleDiscard}
        isApproving={approve.isPending}
      />
    )
  }

  if (summarise.isError) {
    return (
      <div className="space-y-4">
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          Summarisation failed. Please try again.
        </div>
        <button
          type="button"
          className="text-sm text-primary hover:underline"
          onClick={() => summarise.reset()}
        >
          Try again
        </button>
      </div>
    )
  }

  return <SummarisationForm onSubmit={handleSubmit} isPending={summarise.isPending} />
}
```

- [ ] **Step 2: Update the advisor student profile page to pass studentId**

In `frontend/src/pages/advisor/StudentProfile.tsx`, change the `<AISummarisationPanel />` usage to:
```tsx
<AISummarisationPanel studentId={studentId} />
```

- [ ] **Step 3: Run typecheck and lint**

```bash
cd frontend
npm run typecheck
npm run lint
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/advisor/AISummarisationPanel.tsx frontend/src/pages/advisor/StudentProfile.tsx
git commit -m "feat(summarisation): replace placeholder panel with live AI summarisation in advisor profile"
```

---

## Task 9: Admin standalone summarise page and routing

**Files:**
- Create: `frontend/src/pages/admin/Summarise.tsx`
- Modify: `frontend/src/router.tsx`
- Modify: `frontend/src/components/layout/Sidebar.tsx`

- [ ] **Step 1: Create the standalone admin page**

Create `frontend/src/pages/admin/Summarise.tsx`:
```tsx
import { useState } from 'react'

import { Card, CardTitle } from '@/components/ui/Card'
import { SummarisationForm } from '@/features/summarisation/SummarisationForm'
import { SummarisationResult } from '@/features/summarisation/SummarisationResult'
import { useApproveSummarisationMutation, useSummariseMutation } from '@/hooks/useSummarisation'

export function AdminSummarisePage() {
  const summarise = useSummariseMutation()
  const [summarisationId, setSummarisationId] = useState<string | null>(null)
  const approve = useApproveSummarisationMutation(summarisationId ?? '')
  const [success, setSuccess] = useState(false)

  const handleSubmit = (rawText: string) => {
    setSuccess(false)
    summarise.mutate(
      { raw_text: rawText },
      { onSuccess: (data) => setSummarisationId(data.id) },
    )
  }

  const handleApprove = (output: {
    key_issues: string[]
    recommended_actions: string[]
    urgency_level: string
  }) => {
    approve.mutate(output, {
      onSuccess: () => {
        setSuccess(true)
        setSummarisationId(null)
        summarise.reset()
      },
    })
  }

  const handleDiscard = () => {
    setSummarisationId(null)
    summarise.reset()
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardTitle>AI note summarisation</CardTitle>
        <p className="mt-2 text-sm text-neutral-600">
          Paste advising notes, meeting minutes, or helpdesk tickets to generate a structured summary.
          Review and edit the result before saving.
        </p>
        <div className="mt-4">
          {success ? (
            <div className="space-y-4">
              <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
                Summary approved and saved.
              </div>
              <button
                type="button"
                className="text-sm text-primary hover:underline"
                onClick={() => setSuccess(false)}
              >
                Summarise another note
              </button>
            </div>
          ) : summarise.data && summarisationId ? (
            <SummarisationResult
              keyIssues={summarise.data.ai_output.key_issues}
              recommendedActions={summarise.data.ai_output.recommended_actions}
              urgencyLevel={summarise.data.ai_output.urgency_level}
              onApprove={handleApprove}
              onDiscard={handleDiscard}
              isApproving={approve.isPending}
            />
          ) : summarise.isError ? (
            <div className="space-y-4">
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
                Summarisation failed. Please try again.
              </div>
              <button
                type="button"
                className="text-sm text-primary hover:underline"
                onClick={() => summarise.reset()}
              >
                Try again
              </button>
            </div>
          ) : (
            <SummarisationForm onSubmit={handleSubmit} isPending={summarise.isPending} />
          )}
        </div>
      </Card>
    </div>
  )
}
```

- [ ] **Step 2: Add route to router**

In `frontend/src/router.tsx`, add import:
```typescript
import { AdminSummarisePage } from '@/pages/admin/Summarise'
```

Add route inside the admin `<Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>` block, after the `ai-foundation` route:
```tsx
<Route path="/admin/summarise" element={<AdminSummarisePage />} />
```

- [ ] **Step 3: Add sidebar link**

In `frontend/src/components/layout/Sidebar.tsx`, add to the admin `Insights` group items array after the `AI Foundation` entry:
```typescript
{ label: 'Summarise', icon: DocumentTextIcon, to: '/admin/summarise' },
```

- [ ] **Step 4: Run typecheck, lint, and build**

```bash
cd frontend
npm run typecheck
npm run lint
npm run build
```

Expected: All pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/admin/Summarise.tsx frontend/src/router.tsx frontend/src/components/layout/Sidebar.tsx
git commit -m "feat(summarisation): add standalone admin summarise page with sidebar navigation"
```

---

## Task 10: Frontend tests

**Files:**
- Create: `frontend/src/features/summarisation/__tests__/SummarisationForm.test.tsx`
- Create: `frontend/src/features/summarisation/__tests__/SummarisationResult.test.tsx`

- [ ] **Step 1: Create form component test**

```bash
mkdir -p frontend/src/features/summarisation/__tests__
```

Create `frontend/src/features/summarisation/__tests__/SummarisationForm.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { SummarisationForm } from '../SummarisationForm'

describe('SummarisationForm', () => {
  it('renders governance notice', () => {
    render(<SummarisationForm onSubmit={vi.fn()} isPending={false} />)
    expect(screen.getByText(/AI-generated summaries must be reviewed/)).toBeInTheDocument()
  })

  it('renders character counter', () => {
    render(<SummarisationForm onSubmit={vi.fn()} isPending={false} />)
    expect(screen.getByText('0 / 5000')).toBeInTheDocument()
  })

  it('disables button when input is empty', () => {
    render(<SummarisationForm onSubmit={vi.fn()} isPending={false} />)
    expect(screen.getByRole('button', { name: /generate summary/i })).toBeDisabled()
  })

  it('calls onSubmit with text when button clicked', async () => {
    const onSubmit = vi.fn()
    render(<SummarisationForm onSubmit={onSubmit} isPending={false} />)
    const textarea = screen.getByLabelText(/raw advising notes/i)
    await userEvent.type(textarea, 'Student missed three classes.')
    await userEvent.click(screen.getByRole('button', { name: /generate summary/i }))
    expect(onSubmit).toHaveBeenCalledWith('Student missed three classes.')
  })

  it('shows truncation warning when over limit', async () => {
    render(<SummarisationForm onSubmit={vi.fn()} isPending={false} />)
    const textarea = screen.getByLabelText(/raw advising notes/i)
    await userEvent.type(textarea, 'x'.repeat(5001))
    expect(screen.getByText(/exceeds the 5000 character limit/)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Create result component test**

Create `frontend/src/features/summarisation/__tests__/SummarisationResult.test.tsx`:
```tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { SummarisationResult } from '../SummarisationResult'

describe('SummarisationResult', () => {
  const defaultProps = {
    keyIssues: ['Issue one', 'Issue two'],
    recommendedActions: ['Action one'],
    urgencyLevel: 'Routine',
    onApprove: vi.fn(),
    onDiscard: vi.fn(),
    isApproving: false,
  }

  it('renders editable issues', () => {
    render(<SummarisationResult {...defaultProps} />)
    expect(screen.getByDisplayValue('Issue one')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Issue two')).toBeInTheDocument()
  })

  it('renders urgency selector', () => {
    render(<SummarisationResult {...defaultProps} />)
    expect(screen.getByDisplayValue('Routine')).toBeInTheDocument()
  })

  it('calls onApprove with edited data', async () => {
    const onApprove = vi.fn()
    render(<SummarisationResult {...defaultProps} onApprove={onApprove} />)
    await userEvent.click(screen.getByRole('button', { name: /approve and save/i }))
    expect(onApprove).toHaveBeenCalledWith({
      key_issues: ['Issue one', 'Issue two'],
      recommended_actions: ['Action one'],
      urgency_level: 'Routine',
    })
  })

  it('calls onDiscard when discard clicked', async () => {
    const onDiscard = vi.fn()
    render(<SummarisationResult {...defaultProps} onDiscard={onDiscard} />)
    await userEvent.click(screen.getByRole('button', { name: /discard/i }))
    expect(onDiscard).toHaveBeenCalled()
  })

  it('allows adding items up to 5', () => {
    render(<SummarisationResult {...defaultProps} />)
    const addButtons = screen.getAllByText(/\+ add item/i)
    expect(addButtons.length).toBeGreaterThan(0)
  })
})
```

- [ ] **Step 3: Run frontend tests**

```bash
cd frontend
npm run test
```

Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/features/summarisation/__tests__/
git commit -m "test(summarisation): add frontend component tests for form and result"
```

---

## Task 11: Full verification and documentation

**Files:**
- Modify: `docs/phases/phase-04-ai-foundation/README.md`
- Modify: `docs/phases/phase-04-ai-foundation/CHANGELOG.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Run full backend verification**

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
pytest apps/summarisation/tests/ -v
pytest apps/copilot/tests/ -v
ruff check .
```

Expected: All pass, no new migrations needed.

- [ ] **Step 2: Run full frontend verification**

```bash
cd frontend
npm run typecheck
npm run lint
npm run test
npm run build
```

Expected: All pass.

- [ ] **Step 3: Update Phase 4 README with Step 4.3 section**

Add Step 4.3 documentation to `docs/phases/phase-04-ai-foundation/README.md` after the Step 4.2 section, before the "Run And Test Step 4.2" heading.

- [ ] **Step 4: Update Phase 4 CHANGELOG**

Add Step 4.3 entries to `docs/phases/phase-04-ai-foundation/CHANGELOG.md`.

- [ ] **Step 5: Update root CHANGELOG**

Add Step 4.3 entry to `CHANGELOG.md`.

- [ ] **Step 6: Final commit**

```bash
git add docs/
git commit -m "docs(summarisation): add Step 4.3 documentation and changelog entries"
```

- [ ] **Step 7: Squash or keep commits, push to remote**

```bash
git push origin <branch-name>
```

---

## Verification Commands (End-to-End)

After all tasks are complete, the following sequence tests the full flow:

```bash
# Backend
cd backend
source ../.env.local
python manage.py migrate
python manage.py seed_summarisation_demo
python manage.py check
pytest apps/summarisation/tests/ -v
ruff check apps/summarisation/

# Frontend
cd ../frontend
npm run typecheck
npm run lint
npm run test
npm run build
```

## Demo Login Credentials

```
advisor.demo1 / DemoPass123!   (advisor role — can use summarisation in student profile)
admin / DemoPass123!           (admin role — can use /admin/summarise standalone page)
```

## UI Test Paths

1. Login as `advisor.demo1` → navigate to advisor dashboard → click any student → scroll to "AI note summarisation" card → paste text → click "Generate summary" → edit fields → click "Approve and save"
2. Login as admin → sidebar "Summarise" under Insights → paste text → generate → review → approve
