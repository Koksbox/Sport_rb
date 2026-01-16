# apps/athletes/models/medical.py
from django.db import models
from apps.core.models.encryption import EncryptedTextField
from .profile import AthleteProfile

class MedicalData(models.Model):
    athlete = models.OneToOneField(AthleteProfile, on_delete=models.CASCADE, related_name='medical_data')
    has_asthma = models.BooleanField(default=False)
    has_heart_issues = models.BooleanField(default=False)
    has_musculoskeletal_issues = models.BooleanField(default=False)
    other_conditions = EncryptedTextField(blank=True)
    allergies = EncryptedTextField(blank=True)
    emergency_contact_name = EncryptedTextField()
    emergency_contact_phone = EncryptedTextField()