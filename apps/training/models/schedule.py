from django.db import models
from apps.core.models.base import TimeStampedModel
from .group import TrainingGroup

class Schedule(TimeStampedModel):
    group = models.ForeignKey(TrainingGroup, on_delete=models.CASCADE)
    weekday = models.PositiveSmallIntegerField()  # 0=Mon, 6=Sun
    start_time = models.TimeField()
    duration_minutes = models.PositiveSmallIntegerField()