# apps/athletes/admin.py
from django.contrib import admin
from .models import AthleteProfile, MedicalInfo, EmergencyContact, SocialStatus, AthleteSpecialization, SectionEnrollmentRequest


@admin.register(AthleteProfile)
class AthleteProfileAdmin(admin.ModelAdmin):
    """Админка для профилей спортсменов"""
    list_display = ('user', 'main_sport', 'city', 'health_group', 'created_at')
    list_filter = ('main_sport', 'city', 'health_group', 'created_at')
    search_fields = ('user__email', 'user__last_name', 'user__first_name', 'main_sport__name')
    raw_id_fields = ('user', 'city', 'main_sport')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'city', 'main_sport', 'health_group', 'goals')
        }),
        ('Дополнительно', {
            'fields': ('bio', 'achievements', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MedicalInfo)
class MedicalInfoAdmin(admin.ModelAdmin):
    """Админка для медицинской информации"""
    list_display = ('athlete', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('athlete__user__email', 'athlete__user__last_name')
    raw_id_fields = ('athlete',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    """Админка для контактов экстренной связи"""
    list_display = ('athlete', 'full_name', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('athlete__user__email', 'full_name', 'phone')
    raw_id_fields = ('athlete',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SocialStatus)
class SocialStatusAdmin(admin.ModelAdmin):
    """Админка для социального статуса"""
    list_display = ('athlete', 'status', 'document_path', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('athlete__user__email', 'document_path')
    raw_id_fields = ('athlete',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AthleteSpecialization)
class AthleteSpecializationAdmin(admin.ModelAdmin):
    """Админка для специализаций спортсменов"""
    list_display = ('athlete', 'sport', 'is_primary', 'created_at')
    list_filter = ('sport', 'is_primary', 'created_at')
    search_fields = ('athlete__user__email', 'sport__name')
    raw_id_fields = ('athlete', 'sport')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SectionEnrollmentRequest)
class SectionEnrollmentRequestAdmin(admin.ModelAdmin):
    """Админка для заявок на секцию"""
    list_display = ('athlete', 'organization', 'sport_direction', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('athlete__user__email', 'organization__name', 'sport_direction__sport__name')
    raw_id_fields = ('athlete', 'organization', 'sport_direction', 'assigned_group')
    readonly_fields = ('created_at', 'updated_at', 'responded_at')
