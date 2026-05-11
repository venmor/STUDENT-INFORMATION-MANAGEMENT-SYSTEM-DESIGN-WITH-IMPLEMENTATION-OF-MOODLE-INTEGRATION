from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.documents.validators import (
    calculate_sha256,
    sanitize_original_filename,
    validate_document_upload,
)


def test_sanitize_original_filename_removes_paths_and_unsafe_characters():
    assert sanitize_original_filename("../../National ID 2026.pdf") == "National_ID_2026.pdf"
    assert sanitize_original_filename(r"C:\unsafe\appeal letter.docx") == "appeal_letter.docx"
    assert sanitize_original_filename("") == "document"


def test_validate_document_upload_accepts_allowed_pdf(settings):
    settings.STUDENT_DOCUMENT_MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    uploaded_file = SimpleUploadedFile(
        "transcript.pdf",
        b"%PDF-1.4\nsafe\n%%EOF",
        content_type="application/pdf",
    )

    validate_document_upload(uploaded_file)


@pytest.mark.parametrize(
    ("filename", "content_type", "message"),
    [
        ("script.exe", "application/pdf", "Unsupported file extension"),
        ("transcript.pdf", "text/plain", "Unsupported content type"),
    ],
)
def test_validate_document_upload_rejects_unsupported_files(settings, filename, content_type, message):
    settings.STUDENT_DOCUMENT_MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    uploaded_file = SimpleUploadedFile(filename, b"not empty", content_type=content_type)

    with pytest.raises(ValidationError, match=message):
        validate_document_upload(uploaded_file)


def test_validate_document_upload_rejects_empty_files(settings):
    settings.STUDENT_DOCUMENT_MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    uploaded_file = SimpleUploadedFile("empty.pdf", b"", content_type="application/pdf")

    with pytest.raises(ValidationError, match="empty"):
        validate_document_upload(uploaded_file)


def test_validate_document_upload_rejects_oversized_files(settings):
    settings.STUDENT_DOCUMENT_MAX_UPLOAD_SIZE = 4
    uploaded_file = SimpleUploadedFile("large.pdf", b"12345", content_type="application/pdf")

    with pytest.raises(ValidationError, match="exceeds"):
        validate_document_upload(uploaded_file)


def test_calculate_sha256_returns_stable_digest():
    uploaded_file = SimpleUploadedFile("document.pdf", b"stable", content_type="application/pdf")

    assert calculate_sha256(uploaded_file) == "f379ccb92b9116442dc65bdc35648a85d3786b34779db7f704a901fa07b00cb6"
    assert uploaded_file.tell() == 0
