from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.athletes.models.profile import AthleteProfile

GTO_LEVELS = ['1', '2', '3', 'Юный', 'Готов к труду и обороне']

class GtoResult(TimeStampedModel):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=[(l, l) for l in GTO_LEVELS])
    passed_at = models.DateField()
    certificate_number = models.CharField(max_length=50, blank=True)