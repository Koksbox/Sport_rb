# apps/achievements/admin.py
from django.contrib import admin
from .models import Achievement, GtoResult, SportsRank


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Админка для достижений"""
    list_display = ('athlete', 'achievement_type', 'title', 'event', 'date', 'created_at')
    list_filter = ('achievement_type', 'date', 'created_at')
    search_fields = ('athlete__user__email', 'athlete__user__last_name', 'title', 'event__title')
    raw_id_fields = ('athlete', 'event')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GtoResult)
class GtoResultAdmin(admin.ModelAdmin):
    """Админка для результатов ГТО"""
    list_display = ('athlete', 'level', 'badge', 'completion_date', 'protocol_number', 'created_at')
    list_filter = ('level', 'badge', 'completion_date', 'created_at')
    search_fields = ('athlete__user__email', 'athlete__user__last_name', 'protocol_number')
    raw_id_fields = ('athlete',)
    date_hierarchy = 'completion_date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SportsRank)
class SportsRankAdmin(admin.ModelAdmin):
    """Админка для спортивных разрядов"""
    list_display = ('athlete', 'rank', 'issued_by', 'issue_date', 'created_at')
    list_filter = ('rank', 'issue_date', 'created_at')
    search_fields = ('athlete__user__email', 'athlete__user__last_name', 'issued_by')
    raw_id_fields = ('athlete',)
    date_hierarchy = 'issue_date'
    readonly_fields = ('created_at', 'updated_at')
