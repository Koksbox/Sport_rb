# apps/attendance/admin.py
from django.contrib import admin
from .models import AttendanceRecord, AbsenceReason


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    """Админка для записей посещаемости"""
    list_display = ('athlete', 'group', 'date', 'status', 'comment', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('athlete__user__email', 'athlete__user__last_name', 'group__name', 'comment')
    raw_id_fields = ('athlete', 'group')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AbsenceReason)
class AbsenceReasonAdmin(admin.ModelAdmin):
    """Админка для причин отсутствия"""
    list_display = ('name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
