from django.db import models
from apps.core.models.base import TimeStampedModel
from .event import Event
from apps.athletes.models.profile import AthleteProfile

class EventResult(TimeStampedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE)
    place = models.PositiveSmallIntegerField(null=True, blank=True)
    result_text = models.CharField(max_length=100, blank=True)