# apps/events/models/registration.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .event import Event
from apps.athletes.models.profile import AthleteProfile

REGISTRATION_STATUS_CHOICES = [
    ('registered', 'Зарегистрирован'),
    ('confirmed', 'Подтверждён'),
    ('cancelled', 'Отменён'),
]

class EventRegistration(TimeStampedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=REGISTRATION_STATUS_CHOICES, default='registered')

    class Meta:
        db_table = 'events_registration'
        unique_together = ('event', 'athlete')