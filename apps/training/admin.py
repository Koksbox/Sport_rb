# apps/training/admin.py
from django.contrib import admin
from .models import TrainingGroup, Schedule, Enrollment, AgeLevel


@admin.register(TrainingGroup)
class TrainingGroupAdmin(admin.ModelAdmin):
    """Админка для тренировочных групп"""
    list_display = ('name', 'organization', 'sport', 'age_level', 'is_active', 'created_at')
    list_filter = ('sport', 'organization', 'is_active', 'created_at')
    search_fields = ('name', 'organization__name', 'sport__name', 'description')
    raw_id_fields = ('organization', 'sport', 'age_level')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """Админка для расписания тренировок"""
    list_display = ('group', 'weekday', 'start_time', 'end_time', 'location', 'created_at')
    list_filter = ('weekday', 'group__sport', 'group__organization', 'created_at')
    search_fields = ('group__name', 'location')
    raw_id_fields = ('group',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Админка для записей в группы"""
    list_display = ('athlete', 'group', 'status', 'joined_at', 'created_at')
    list_filter = ('status', 'joined_at', 'created_at')
    search_fields = ('athlete__user__email', 'athlete__user__last_name', 'group__name')
    raw_id_fields = ('athlete', 'group')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AgeLevel)
class AgeLevelAdmin(admin.ModelAdmin):
    """Админка для возрастных уровней"""
    list_display = ('name', 'min_age', 'max_age', 'created_at')
    list_filter = ('min_age', 'max_age', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
