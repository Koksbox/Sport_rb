from django.db import models
from apps.core.models.base import TimeStampedModel, SoftDeleteModel
from apps.geography.models import City
from apps.users.models.user import CustomUser

ORG_TYPE_CHOICES = [('state', 'Государственная'), ('private', 'Частная')]

class Organization(TimeStampedModel, SoftDeleteModel):
    name = models.CharField(max_length=255)
    org_type = models.CharField(max_length=20, choices=ORG_TYPE_CHOICES)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    website = models.URLField(blank=True)
    inn = models.CharField(max_length=12, unique=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='verified_organizations'
    )
    is_accessible = models.BooleanField(default=False)  # ♿️
    is_priority = models.BooleanField(default=False)   # Приоритетная секция

    def __str__(self):
        return self.name