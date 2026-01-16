from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.athletes.models.profile import AthleteProfile
from apps.training.models.group import TrainingGroup

ATTENDANCE_CHOICES = [('present', 'Присутствовал'), ('absent', 'Отсутствовал'), ('late', 'Опоздал')]

class AttendanceRecord(TimeStampedModel):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE)
    group = models.ForeignKey(TrainingGroup, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES)
    comment = models.TextField(blank=True)