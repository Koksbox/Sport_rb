from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.coaches.models.coach_profile import CoachProfile
from apps.organizations.models.organization import Organization
from apps.training.models.age_level import AgeLevel

MEMBERSHIP_STATUS = [('pending', 'Ожидает подтверждения'), ('active', 'Активен'), ('archived', 'Архив')]

class CoachMembership(TimeStampedModel):
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='pending')
    age_groups = models.ManyToManyField(AgeLevel, blank=True)