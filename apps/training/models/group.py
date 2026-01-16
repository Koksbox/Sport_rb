# apps/training/models/group.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.organizations.models.organization import Organization
from apps.sports.models.sport import Sport
from .age_level import AgeLevel

class TrainingGroup(TimeStampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=100)
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
    age_level = models.ForeignKey(AgeLevel, on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'training_group'
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return f"{self.name} ({self.organization.name})"