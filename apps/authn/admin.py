# apps/authn/admin.py
from django.contrib import admin
from .models import AuthProvider


@admin.register(AuthProvider)
class AuthProviderAdmin(admin.ModelAdmin):
    """Админка для провайдеров аутентификации"""
    list_display = ('user', 'provider', 'external_id', 'created_at')
    list_filter = ('provider', 'created_at')
    search_fields = ('user__email', 'user__last_name', 'external_id')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
