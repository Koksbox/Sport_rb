# apps/organizations/models/verification.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .organization import Organization
from apps.users.models.user import CustomUser

class VerificationRequest(TimeStampedModel):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'На проверке'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ])
    rejection_reason = models.TextField(blank=True)

    class Meta:
        db_table = 'organizations_verificationrequest'