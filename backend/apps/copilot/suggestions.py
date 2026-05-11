from __future__ import annotations

from typing import Any

from .models import CopilotConfidence


def suggested_next_actions_for_question(
    question: str,
    *,
    sources: list[dict[str, Any]],
    confidence: str,
) -> list[dict[str, str]]:
    lowered = question.lower()
    source_types = {source.get("sourceType") for source in sources}
    actions: list[dict[str, str]] = []
    if "document" in lowered or "rejected" in lowered or "upload" in lowered:
        actions.append({"label": "Open Documents", "url": "/documents"})
    if "grade" in lowered or "transcript" in lowered:
        actions.append({"label": "Open My Grades", "url": "/student/grades"})
    if "course" in lowered or "enrolled" in lowered:
        actions.append({"label": "Open My Courses", "url": "/student/courses"})
    if "register" in lowered or "registration" in lowered:
        actions.append({"label": "Open Registration", "url": "/student/register"})
    if (
        "deadline" in lowered
        or "calendar" in lowered
        or "drop" in lowered
        or "registration" in lowered
        or "ACADEMIC_CALENDAR" in source_types
    ):
        actions.append({"label": "Open Academic Calendar", "url": "/calendar"})
    if "notification" in lowered:
        actions.append({"label": "Open Notifications", "url": "/notifications"})
    if confidence in {CopilotConfidence.LOW, CopilotConfidence.UNSUPPORTED}:
        actions.append({"label": "Verify with Registrar", "url": "/calendar"})
    if not actions:
        actions.append({"label": "Open Academic Calendar", "url": "/calendar"})
    return _unique_actions(actions)[:4]


def _unique_actions(actions: list[dict[str, str]]) -> list[dict[str, str]]:
    unique: list[dict[str, str]] = []
    seen = set()
    for action in actions:
        if action["label"] in seen:
            continue
        seen.add(action["label"])
        unique.append(action)
    return unique
