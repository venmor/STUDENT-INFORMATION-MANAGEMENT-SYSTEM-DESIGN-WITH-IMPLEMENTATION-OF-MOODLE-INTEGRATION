from django.contrib import admin

from .models import StudentDocument


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "document_type", "visibility", "status", "uploaded_by", "created_at")
    list_filter = ("document_type", "visibility", "status", "created_at")
    search_fields = ("title", "description", "original_filename", "student__student_number", "student__user__full_name")
    readonly_fields = ("id", "created_at", "updated_at", "checksum_sha256", "file_size", "content_type")
