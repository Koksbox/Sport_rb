from django.db import models
from apps.core.models.base import TimeStampedModel
from .sport import Sport

class SportCategory(TimeStampedModel):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)