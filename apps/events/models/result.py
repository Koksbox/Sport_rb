# apps/events/models/result.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .event import Event
from apps.athletes.models.profile import AthleteProfile

class EventResult(TimeStampedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='results')
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE)
    place = models.PositiveSmallIntegerField(null=True, blank=True)  # 1, 2, 3...
    result_value = models.CharField(max_length=100, blank=True)  # "12.5 сек", "5.2 м"
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'events_result'
        unique_together = ('event', 'athlete')