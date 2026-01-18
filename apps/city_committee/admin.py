# apps/city_committee/admin.py
from django.contrib import admin
from .models import CommitteeStaff, CityPermission, ManagedEvent


@admin.register(CommitteeStaff)
class CommitteeStaffAdmin(admin.ModelAdmin):
    """Админка для сотрудников городского комитета"""
    list_display = ('user', 'city', 'created_at')
    list_filter = ('city', 'created_at')
    search_fields = ('user__email', 'user__last_name', 'user__first_name')
    raw_id_fields = ('user', 'city')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CityPermission)
class CityPermissionAdmin(admin.ModelAdmin):
    """Админка для разрешений городского комитета"""
    list_display = ('staff', 'organization', 'can_manage', 'created_at')
    list_filter = ('can_manage', 'created_at')
    search_fields = ('staff__user__email', 'organization__name')
    raw_id_fields = ('staff', 'organization')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ManagedEvent)
class ManagedEventAdmin(admin.ModelAdmin):
    """Админка для управляемых мероприятий"""
    list_display = ('event', 'managed_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('event__title', 'managed_by__user__email')
    raw_id_fields = ('event', 'managed_by')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
