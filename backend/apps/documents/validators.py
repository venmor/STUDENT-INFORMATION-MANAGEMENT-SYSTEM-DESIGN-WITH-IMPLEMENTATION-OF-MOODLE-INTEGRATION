from __future__ import annotations

import hashlib
import ntpath
import os
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import get_valid_filename


ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}
ALLOWED_DOCUMENT_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
DEFAULT_MAX_UPLOAD_SIZE = 10 * 1024 * 1024


def max_upload_size() -> int:
    return int(getattr(settings, "STUDENT_DOCUMENT_MAX_UPLOAD_SIZE", DEFAULT_MAX_UPLOAD_SIZE))


def sanitize_original_filename(filename: str | None) -> str:
    raw_filename = str(filename or "").strip()
    if not raw_filename:
        return "document"
    basename = ntpath.basename(os.path.basename(raw_filename))
    safe = get_valid_filename(basename).strip("._")
    return safe[:255] or "document"


def validate_document_upload(uploaded_file) -> None:
    filename = sanitize_original_filename(getattr(uploaded_file, "name", ""))
    extension = Path(filename).suffix.lower()
    content_type = (getattr(uploaded_file, "content_type", "") or "").lower()
    file_size = int(getattr(uploaded_file, "size", 0) or 0)

    if file_size <= 0:
        raise ValidationError("Uploaded document cannot be empty.")
    if file_size > max_upload_size():
        raise ValidationError(f"Uploaded document exceeds the {max_upload_size() // (1024 * 1024)} MB size limit.")
    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError("Unsupported file extension.")
    if content_type not in ALLOWED_DOCUMENT_CONTENT_TYPES:
        raise ValidationError("Unsupported content type.")


def calculate_sha256(uploaded_file) -> str:
    digest = hashlib.sha256()
    current_position = uploaded_file.tell() if hasattr(uploaded_file, "tell") else 0
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    for chunk in uploaded_file.chunks() if hasattr(uploaded_file, "chunks") else [uploaded_file.read()]:
        digest.update(chunk)
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(current_position)
    return digest.hexdigest()
