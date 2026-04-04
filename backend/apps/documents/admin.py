from django.contrib import admin

from apps.documents.models import DocumentVersion, LandDocumentChecklistItem


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    raw_id_fields = ("uploaded_by", "created_by", "updated_by", "deleted_by")


@admin.register(LandDocumentChecklistItem)
class LandDocumentChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("id", "land", "document_kind", "checklist_status", "is_deleted")
    list_filter = ("document_kind", "checklist_status", "is_deleted")
    inlines = [DocumentVersionInline]
    raw_id_fields = ("land", "created_by", "updated_by", "deleted_by")


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ("id", "checklist_item", "version_number", "s3_key", "created_at")
    raw_id_fields = (
        "checklist_item",
        "uploaded_by",
        "created_by",
        "updated_by",
        "deleted_by",
    )
