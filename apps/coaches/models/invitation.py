# apps/coaches/models/invitation.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .coach_profile import CoachProfile
from apps.organizations.models.organization import Organization
from apps.sports.models.sport import Sport
from apps.training.models.age_level import AgeLevel

class CoachInvitation(TimeStampedModel):
    """Приглашение от директора организации тренеру на работу"""
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, related_name='invitations')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='coach_invitations')
    specialization = models.ForeignKey(Sport, on_delete=models.PROTECT, null=True, blank=True)
    age_levels = models.ManyToManyField(AgeLevel, blank=True)
    message = models.TextField(blank=True, help_text="Сообщение от директора с условиями работы")
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Ожидает ответа'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ])
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'coaches_coachinvitation'
        unique_together = ('coach', 'organization')
        ordering = ['-created_at']

    def __str__(self):
        return f"Приглашение {self.organization.name} → {self.coach.user.get_full_name()}"
