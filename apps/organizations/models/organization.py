# apps/organizations/models/organization.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.geography.models.city import City
from apps.users.models import CustomUser

ORG_STATUS_CHOICES = [
    ('pending', 'Ожидает модерации'),
    ('approved', 'Одобрено'),
    ('rejected', 'Отклонено'),
]

class Organization(TimeStampedModel):
    name = models.CharField(max_length=255)
    org_type = models.CharField(max_length=20, choices=[
        ('state', 'Государственная'),
        ('private', 'Частная'),
    ])
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='organizations')
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    website = models.URLField(blank=True)
    inn = models.CharField(max_length=12, unique=True)
    status = models.CharField(max_length=20, choices=ORG_STATUS_CHOICES, default='pending')  # ← ДОБАВЛЕНО
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_organizations')
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'organizations_organization'

    def __str__(self):
        return self.name