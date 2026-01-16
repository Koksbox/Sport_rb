# apps/organizations/staff/coach_membership.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.coaches.models.coach_profile import CoachProfile
from apps.organizations.models.organization import Organization
from apps.training.models.group import TrainingGroup

MEMBERSHIP_STATUS_CHOICES = [
    ('active', 'Активен'),
    ('archived', 'Архив'),
]

class CoachMembership(TimeStampedModel):
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS_CHOICES, default='active')
    groups = models.ManyToManyField(TrainingGroup, blank=True)

    class Meta:
        db_table = 'organizations_coachmembership'
        unique_together = ('coach', 'organization')