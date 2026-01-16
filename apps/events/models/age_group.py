# apps/events/models/age_group.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .event import Event

class EventAgeGroup(TimeStampedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='age_groups')
    min_age = models.PositiveSmallIntegerField()
    max_age = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'events_agegroup'