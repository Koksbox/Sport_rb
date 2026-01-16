# apps/events/models/participation.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .event import Event
from apps.athletes.models.profile import AthleteProfile

class EventParticipation(TimeStampedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)

    class Meta:
        db_table = 'events_participation'
        unique_together = ('event', 'athlete')