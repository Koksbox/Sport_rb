# apps/organizations/models/accessibility.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .organization import Organization

class Accessibility(TimeStampedModel):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='accessibility')
    wheelchair_access = models.BooleanField(default=False)
    adapted_restroom = models.BooleanField(default=False)
    sign_language_support = models.BooleanField(default=False)
    other_info = models.TextField(blank=True)

    class Meta:
        db_table = 'organizations_accessibility'