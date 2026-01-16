from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.athletes.models.profile import AthleteProfile
from apps.events.models.event import Event

class Achievement(TimeStampedModel):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_achieved = models.DateField()
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)