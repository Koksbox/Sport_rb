from django.db import models
from apps.core.models.base import TimeStampedModel
from .organization import Organization
from apps.users.models.user import CustomUser

class VerificationRequest(TimeStampedModel):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')  # pending, approved, rejected
    rejection_reason = models.TextField(blank=True)