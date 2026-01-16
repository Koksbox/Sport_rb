# apps/attendance/models/absence_reason.py
from django.db import models
from apps.core.models.base import TimeStampedModel

class AbsenceReason(TimeStampedModel):
    name = models.CharField(max_length=100)  # "Болезнь", "Семейные обстоятельства"

    class Meta:
        db_table = 'attendance_absencereason'

    def __str__(self):
        return self.name