# apps/geography/admin.py
from django.contrib import admin
from .models import Region, City, District


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    """Админка для регионов"""
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Админка для городов"""
    list_display = ('name', 'region', 'created_at')
    list_filter = ('region', 'created_at')
    search_fields = ('name', 'region__name')
    raw_id_fields = ('region',)
    ordering = ('region', 'name')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    """Админка для районов"""
    list_display = ('name', 'city', 'created_at')
    list_filter = ('city', 'created_at')
    search_fields = ('name', 'city__name')
    raw_id_fields = ('city',)
    ordering = ('city', 'name')
