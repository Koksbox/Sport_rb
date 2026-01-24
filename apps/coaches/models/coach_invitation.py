# apps/coaches/models/coach_invitation.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .coach_profile import CoachProfile
from apps.organizations.models.organization import Organization
from apps.sports.models import Sport
from apps.training.models.age_level import AgeLevel

class CoachInvitation(TimeStampedModel):
    """Приглашение от директора организации к тренеру"""
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, related_name='invitations')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='coach_invitations')
    specialization = models.ForeignKey(Sport, on_delete=models.PROTECT)
    age_levels = models.ManyToManyField(AgeLevel, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Ожидает ответа'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ])
    invited_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='sent_invitations',
        help_text='Директор, отправивший приглашение'
    )

    class Meta:
        db_table = 'coaches_coachinvitation'
        unique_together = ('coach', 'organization')
        ordering = ['-created_at']

    def __str__(self):
        return f"Приглашение {self.coach.user.get_full_name()} в {self.organization.name}"
