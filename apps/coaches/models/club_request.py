# apps/coaches/models/club_request.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .coach_profile import CoachProfile
from apps.organizations.models.organization import Organization
from apps.sports.models.sport import Sport

REQUEST_STATUS_CHOICES = [
    ('pending', 'На рассмотрении'),
    ('approved', 'Одобрено'),
    ('rejected', 'Отклонено'),
]

class ClubRequest(TimeStampedModel):
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, related_name='club_requests')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Sport, on_delete=models.PROTECT)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='pending')
    rejected_reason = models.TextField(blank=True)

    class Meta:
        db_table = 'coaches_clubrequest'
        unique_together = ('coach', 'organization')  # один запрос на клуб