# apps/training/models/enrollment.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .group import TrainingGroup
from apps.athletes.models.profile import AthleteProfile

ENROLLMENT_STATUS_CHOICES = [
    ('pending', 'Ожидает подтверждения'),
    ('active', 'Активен'),
    ('rejected', 'Отклонён'),
    ('left', 'Покинул'),
]

class Enrollment(TimeStampedModel):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='enrollments')
    group = models.ForeignKey(TrainingGroup, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS_CHOICES, default='pending')
    joined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'training_enrollment'
        unique_together = ('athlete', 'group')