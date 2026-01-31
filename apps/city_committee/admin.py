# apps/city_committee/admin.py
from django.contrib import admin
from .models import CommitteeStaff, CityPermission, ManagedEvent, CommitteeRegistrationCode


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


@admin.register(CommitteeRegistrationCode)
class CommitteeRegistrationCodeAdmin(admin.ModelAdmin):
    """Админка для кодов регистрации спорткомитета"""
    list_display = ('code', 'city_name', 'department', 'position', 'is_used', 'is_active', 'used_by_email', 'created_at', 'expires_at')
    list_filter = ('is_used', 'is_active', 'city_name', 'created_at', 'expires_at')
    search_fields = ('code', 'city_name', 'department', 'position', 'used_by_email', 'issued_by')
    readonly_fields = ('created_at', 'updated_at', 'used_at', 'used_by_email')
    fieldsets = (
        ('Основная информация', {
            'fields': ('code', 'city_name', 'department', 'position', 'issued_by')
        }),
        ('Статус', {
            'fields': ('is_active', 'is_used', 'used_by_email', 'used_at')
        }),
        ('Срок действия', {
            'fields': ('expires_at',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Делаем код неизменяемым после создания"""
        readonly = list(self.readonly_fields)
        if obj:  # Если объект уже существует
            readonly.append('code')
        return readonly
