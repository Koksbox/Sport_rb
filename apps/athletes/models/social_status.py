# apps/athletes/models/social_status.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .profile import AthleteProfile

SOCIAL_STATUS_CHOICES = [
    ('beneficiary', 'Льготник'),
    ('large_family', 'Многодетная семья'),
    ('disabled', 'ОВЗ'),
    ('orphan', 'Сирота'),
    ('none', 'Нет'),
]

class SocialStatus(TimeStampedModel):
    athlete = models.OneToOneField(AthleteProfile, on_delete=models.CASCADE, related_name='social_status')
    status = models.CharField(max_length=20, choices=SOCIAL_STATUS_CHOICES, default='none')
    document_path = models.CharField(max_length=500, blank=True)  # подтверждение

    class Meta:
        db_table = 'athletes_socialstatus'