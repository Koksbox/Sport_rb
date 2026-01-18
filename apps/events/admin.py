# apps/events/admin.py
from django.contrib import admin
from .models import Event, EventCategory, EventAgeGroup, EventRegistration, EventParticipation, EventResult


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Админка для мероприятий"""
    list_display = ('title', 'event_type', 'level', 'city', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('event_type', 'level', 'status', 'start_date', 'created_at')
    search_fields = ('title', 'description', 'city__name', 'venue')
    raw_id_fields = ('city', 'organizer_org')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'event_type', 'level', 'city', 'venue')
        }),
        ('Даты и время', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Организация', {
            'fields': ('organizer_org', 'requires_registration', 'max_participants')
        }),
        ('Статус', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    """Админка для категорий мероприятий"""
    list_display = ('name', 'description', 'created_at')
    list_filter = ('name', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EventAgeGroup)
class EventAgeGroupAdmin(admin.ModelAdmin):
    """Админка для возрастных групп мероприятий"""
    list_display = ('event', 'min_age', 'max_age', 'created_at')
    list_filter = ('min_age', 'max_age', 'created_at')
    search_fields = ('event__title',)
    raw_id_fields = ('event',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    """Админка для регистраций на мероприятия"""
    list_display = ('event', 'athlete', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('event__title', 'athlete__user__email', 'athlete__user__last_name')
    raw_id_fields = ('event', 'athlete')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    """Админка для участия в мероприятиях"""
    list_display = ('event', 'athlete', 'attended', 'created_at')
    list_filter = ('attended', 'created_at')
    search_fields = ('event__title', 'athlete__user__email')
    raw_id_fields = ('event', 'athlete')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EventResult)
class EventResultAdmin(admin.ModelAdmin):
    """Админка для результатов мероприятий"""
    list_display = ('event', 'athlete', 'place', 'result_value', 'created_at')
    list_filter = ('place', 'created_at')
    search_fields = ('event__title', 'athlete__user__email', 'athlete__user__last_name', 'result_value')
    raw_id_fields = ('event', 'athlete')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
