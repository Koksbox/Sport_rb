from django.db import models
from apps.core.models.base import TimeStampedModel
from .profile import AthleteProfile

class SocialStatus(TimeStampedModel):
    athlete = models.OneToOneField(AthleteProfile, on_delete=models.CASCADE)
    is_beneficiary = models.BooleanField(default=False)
    is_large_family = models.BooleanField(default=False)
    has_disability = models.BooleanField(default=False)
    is_orphan = models.BooleanField(default=False)