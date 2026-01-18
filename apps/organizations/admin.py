# apps/organizations/admin.py
from django.contrib import admin
from .models import Organization, SportDirection, OrganizationDocument, VerificationRequest, PriorityAssignment, Accessibility


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Админка для организаций"""
    list_display = ('name', 'org_type', 'city', 'status', 'verified_at', 'created_at')
    list_filter = ('org_type', 'status', 'verified_at', 'created_at')
    search_fields = ('name', 'inn', 'city__name', 'address')
    raw_id_fields = ('city',)
    date_hierarchy = 'created_at'
    readonly_fields = ('verified_at', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'org_type', 'city', 'address', 'inn', 'ogrn')
        }),
        ('Статус', {
            'fields': ('status', 'verified_at')
        }),
        ('Дополнительно', {
            'fields': ('description', 'website', 'phone', 'email')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SportDirection)
class SportDirectionAdmin(admin.ModelAdmin):
    """Админка для спортивных направлений организаций"""
    list_display = ('organization', 'sport', 'created_at')
    list_filter = ('sport', 'created_at')
    search_fields = ('organization__name', 'sport__name')
    raw_id_fields = ('organization', 'sport')


@admin.register(OrganizationDocument)
class OrganizationDocumentAdmin(admin.ModelAdmin):
    """Админка для документов организаций"""
    list_display = ('organization', 'doc_type', 'file_path', 'created_at')
    list_filter = ('doc_type', 'created_at')
    search_fields = ('organization__name', 'file_path')
    raw_id_fields = ('organization',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    """Админка для запросов на верификацию"""
    list_display = ('organization', 'submitted_by', 'status', 'rejection_reason', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('organization__name', 'submitted_by__email', 'rejection_reason')
    raw_id_fields = ('organization', 'submitted_by')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(PriorityAssignment)
class PriorityAssignmentAdmin(admin.ModelAdmin):
    """Админка для приоритетных назначений"""
    list_display = ('organization', 'assigned_by', 'reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('organization__name', 'reason')
    raw_id_fields = ('organization', 'assigned_by')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Accessibility)
class AccessibilityAdmin(admin.ModelAdmin):
    """Админка для доступности организаций"""
    list_display = ('organization', 'wheelchair_access', 'adapted_restroom', 'sign_language_support', 'created_at')
    list_filter = ('wheelchair_access', 'adapted_restroom', 'sign_language_support', 'created_at')
    search_fields = ('organization__name', 'other_info')
    raw_id_fields = ('organization',)
    readonly_fields = ('created_at', 'updated_at')
