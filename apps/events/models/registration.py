from django.db import models
from apps.core.models.base import TimeStampedModel
from .event import Event
from apps.athletes.models.profile import AthleteProfile

class EventRegistration(TimeStampedModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='registered')