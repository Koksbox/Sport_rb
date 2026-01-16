from django.db import models
from apps.core.models.base import TimeStampedModel
from .user import CustomUser

class Consent(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    consent_type = models.CharField(max_length=50)  # 'pdn_processing', 'marketing'
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()