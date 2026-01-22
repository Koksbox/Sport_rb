# apps/athletes/models/medical.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.core.models.encryption import EncryptedTextField
from .profile import AthleteProfile

MEDICAL_CONDITIONS = [
    'asthma',
    'heart_issues',
    'musculoskeletal_injuries',
]

class MedicalInfo(TimeStampedModel):
    athlete = models.OneToOneField(AthleteProfile, on_delete=models.CASCADE, related_name='medical_info')
    conditions = models.JSONField(default=list)  # список из MEDICAL_CONDITIONS
    other_conditions = EncryptedTextField(blank=True)
    allergies = EncryptedTextField(blank=True)
    health_issues_description = EncryptedTextField(blank=True, help_text="Описание проблем со здоровьем")

    class Meta:
        db_table = 'athletes_medical'