# apps/sports/admin.py
from django.contrib import admin
from .models import Sport, SportCategory


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    """Админка для видов спорта"""
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(SportCategory)
class SportCategoryAdmin(admin.ModelAdmin):
    """Админка для категорий спорта"""
    list_display = ('name', 'sport', 'created_at')
    list_filter = ('sport', 'created_at')
    search_fields = ('name', 'sport__name')
    raw_id_fields = ('sport',)
    ordering = ('sport', 'name')
