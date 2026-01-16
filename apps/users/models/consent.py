# apps/users/models/consent.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .user import CustomUser

class Consent(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='consents')
    type = models.CharField(max_length=50)  # 'fz152_personal', 'fz152_medical', etc.
    granted = models.BooleanField(default=True)

    class Meta:
        db_table = 'users_consent'
        unique_together = ('user', 'type')