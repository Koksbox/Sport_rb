# apps/training/models/schedule.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .group import TrainingGroup

WEEKDAYS = [
    (1, 'Понедельник'),
    (2, 'Вторник'),
    (3, 'Среда'),
    (4, 'Четверг'),
    (5, 'Пятница'),
    (6, 'Суббота'),
    (7, 'Воскресенье'),
]

class Schedule(TimeStampedModel):
    group = models.ForeignKey(TrainingGroup, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'training_schedule'
        ordering = ['weekday', 'start_time']