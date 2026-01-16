from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.core.models.encryption import EncryptedTextField
from .profile import AthleteProfile

class MedicalData(TimeStampedModel):
    athlete = models.OneToOneField(AthleteProfile, on_delete=models.CASCADE)
    conditions = models.JSONField(default=list)  # ['asthma', 'heart_issues', ...]
    other_condition = EncryptedTextField(blank=True)
    allergies = EncryptedTextField(blank=True)
    emergency_contact_name = EncryptedTextField()
    emergency_contact_phone = EncryptedTextField()