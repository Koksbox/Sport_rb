# apps/events/models/registration.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .event import Event
from apps.athletes.models.profile import AthleteProfile
from apps.coaches.models.coach_profile import CoachProfile

REGISTRATION_STATUS_CHOICES = [
    ('registered', 'Зарегистрирован'),
    ('confirmed', 'Подтверждён'),
    ('cancelled', 'Отменён'),
]

REGISTRATION_TYPE_CHOICES = [
    ('athlete', 'Спортсмен'),
    ('coach', 'Тренер'),
]

class EventRegistration(TimeStampedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registration_type = models.CharField(max_length=20, choices=REGISTRATION_TYPE_CHOICES, default='athlete')
    
    # Для спортсменов
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='event_registrations')
    
    # Для тренеров
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='event_registrations')
    
    status = models.CharField(max_length=20, choices=REGISTRATION_STATUS_CHOICES, default='registered')
    
    # Связь с приглашением (если регистрация через приглашение)
    invitation = models.ForeignKey('EventInvitation', on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations')

    class Meta:
        db_table = 'events_registration'
        unique_together = [
            ('event', 'athlete', 'registration_type'),
            ('event', 'coach', 'registration_type'),
        ]
        indexes = [
            models.Index(fields=['status', 'registration_type']),
        ]