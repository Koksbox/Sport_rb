from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.organizations.models.organization import Organization
from apps.sports.models import Sport
from apps.coaches.models.coach_profile import CoachProfile
from .age_level import AgeLevel

class TrainingGroup(TimeStampedModel):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    age_level = models.ForeignKey(AgeLevel, on_delete=models.CASCADE)
    coach = models.ForeignKey(CoachProfile, on_delete=models.SET_NULL, null=True, blank=True)