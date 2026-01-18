# apps/coaches/admin.py
from django.contrib import admin
from .models import CoachProfile, Qualification, ClubRequest


@admin.register(CoachProfile)
class CoachProfileAdmin(admin.ModelAdmin):
    """Админка для профилей тренеров"""
    list_display = ('user', 'specialization', 'city', 'experience_years', 'created_at')
    list_filter = ('specialization', 'city', 'experience_years', 'created_at')
    search_fields = ('user__email', 'user__last_name', 'user__first_name', 'specialization__name')
    raw_id_fields = ('user', 'city', 'specialization')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'city', 'specialization', 'experience_years', 'bio')
        }),
        ('Дополнительно', {
            'fields': ('certificates', 'achievements', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    """Админка для квалификаций тренеров"""
    list_display = ('coach', 'title', 'issued_by', 'issue_date', 'created_at')
    list_filter = ('issue_date', 'created_at')
    search_fields = ('coach__user__email', 'coach__user__last_name', 'title', 'issued_by')
    raw_id_fields = ('coach',)
    date_hierarchy = 'issue_date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ClubRequest)
class ClubRequestAdmin(admin.ModelAdmin):
    """Админка для запросов в клубы"""
    list_display = ('coach', 'organization', 'specialization', 'status', 'created_at')
    list_filter = ('status', 'specialization', 'created_at')
    search_fields = ('coach__user__email', 'organization__name', 'message')
    raw_id_fields = ('coach', 'organization', 'specialization')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
