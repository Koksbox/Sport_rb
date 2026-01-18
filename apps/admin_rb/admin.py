# apps/admin_rb/admin.py
from django.contrib import admin
from .models import SystemRoleAssignment


@admin.register(SystemRoleAssignment)
class SystemRoleAssignmentAdmin(admin.ModelAdmin):
    """Админка для системных ролей"""
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__email', 'user__last_name', 'user__first_name', 'role')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
