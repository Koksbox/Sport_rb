# apps/parents/admin.py
from django.contrib import admin
from .models import ParentProfile, ParentChildLink


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    """Админка для профилей родителей"""
    list_display = ('user', 'created_at')
    search_fields = ('user__email', 'user__last_name', 'user__first_name')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'


@admin.register(ParentChildLink)
class ParentChildLinkAdmin(admin.ModelAdmin):
    """Админка для связей родитель-ребенок"""
    list_display = ('parent', 'child_profile', 'is_confirmed', 'created_at')
    list_filter = ('is_confirmed', 'created_at')
    search_fields = ('parent__email', 'parent__last_name', 'child_profile__user__email', 'child_profile__user__last_name')
    raw_id_fields = ('parent', 'child_profile')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
