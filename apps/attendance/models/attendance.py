# apps/attendance/models/attendance.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.athletes.models.profile import AthleteProfile
from apps.training.models.group import TrainingGroup

ATTENDANCE_STATUS_CHOICES = [
    ('present', 'Присутствовал'),
    ('absent', 'Отсутствовал'),
    ('late', 'Опоздал'),
]

class AttendanceRecord(TimeStampedModel):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE)
    group = models.ForeignKey(TrainingGroup, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS_CHOICES)
    comment = models.TextField(blank=True)  # причина отсутствия

    class Meta:
        db_table = 'attendance_attendance'
        unique_together = ('athlete', 'group', 'date')
        ordering = ['-date']