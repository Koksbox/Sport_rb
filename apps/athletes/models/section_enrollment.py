# apps/athletes/models/section_enrollment.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.athletes.models.profile import AthleteProfile
from apps.organizations.models.organization import Organization
from apps.organizations.models.sport_direction import SportDirection

ENROLLMENT_REQUEST_STATUS_CHOICES = [
    ('pending', 'Ожидает подтверждения'),
    ('approved', 'Одобрено'),
    ('rejected', 'Отклонено'),
]

class SectionEnrollmentRequest(TimeStampedModel):
    """Заявка спортсмена на вступление в секцию (директор решает группу)"""
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='section_enrollment_requests')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='section_enrollment_requests')
    sport_direction = models.ForeignKey(SportDirection, on_delete=models.CASCADE, related_name='enrollment_requests')
    status = models.CharField(max_length=20, choices=ENROLLMENT_REQUEST_STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Сообщение от спортсмена")
    assigned_group = models.ForeignKey(
        'training.TrainingGroup', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='section_enrollment_assignments'
    )
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'athletes_sectionenrollmentrequest'
        unique_together = ('athlete', 'sport_direction', 'status')
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка {self.athlete.user.get_full_name()} в секцию {self.sport_direction.sport.name}"
