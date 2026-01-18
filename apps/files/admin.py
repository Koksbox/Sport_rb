# apps/files/admin.py
from django.contrib import admin
from .models import StoredFile


@admin.register(StoredFile)
class StoredFileAdmin(admin.ModelAdmin):
    """Админка для файлов"""
    list_display = ('original_name', 'category', 'size_bytes', 'mime_type', 'owner', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('original_name', 'owner__email', 'owner__last_name', 'stored_path')
    raw_id_fields = ('owner',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
