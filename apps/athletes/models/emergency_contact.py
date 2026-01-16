# apps/athletes/models/emergency_contact.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .profile import AthleteProfile

class EmergencyContact(TimeStampedModel):
    athlete = models.OneToOneField(AthleteProfile, on_delete=models.CASCADE, related_name='emergency_contact')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)

    class Meta:
        db_table = 'athletes_emergency_contact'