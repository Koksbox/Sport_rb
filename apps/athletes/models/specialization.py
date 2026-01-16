# apps/athletes/models/specialization.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .profile import AthleteProfile
from apps.sports.models.sport import Sport

class AthleteSpecialization(TimeStampedModel):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='specializations')
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'athletes_specialization'
        unique_together = ('athlete', 'sport')