# apps/organizations/models/sport_direction.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.sports.models.sport import Sport
from .organization import Organization

class SportDirection(TimeStampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='sport_directions')
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT)

    class Meta:
        db_table = 'organizations_sportdirection'
        unique_together = ('organization', 'sport')

    def __str__(self):
        return f"{self.organization.name} — {self.sport.name}"