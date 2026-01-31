# apps/events/models/invitation.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .event import Event
from apps.athletes.models.profile import AthleteProfile
from apps.coaches.models.coach_profile import CoachProfile
from apps.users.models.user import CustomUser

INVITATION_STATUS_CHOICES = [
    ('pending', 'Ожидает ответа'),
    ('accepted', 'Принято'),
    ('declined', 'Отклонено'),
    ('expired', 'Истекло'),
]

INVITATION_TYPE_CHOICES = [
    ('athlete', 'Спортсмен'),
    ('coach', 'Тренер'),
]

class EventInvitation(TimeStampedModel):
    """Приглашение на мероприятие"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='invitations')
    invitation_type = models.CharField(max_length=20, choices=INVITATION_TYPE_CHOICES, default='athlete')
    
    # Кто отправил приглашение
    sent_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_event_invitations')
    
    # Для спортсменов
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='event_invitations')
    
    # Для тренеров
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='event_invitations')
    
    status = models.CharField(max_length=20, choices=INVITATION_STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, null=True, help_text='Персональное сообщение к приглашению')
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Для массовых приглашений
    group_id = models.IntegerField(null=True, blank=True, help_text='ID группы, если приглашение массовое')
    organization_id = models.IntegerField(null=True, blank=True, help_text='ID организации, если приглашение массовое')
    
    class Meta:
        db_table = 'events_invitation'
        indexes = [
            models.Index(fields=['status', 'invitation_type']),
            models.Index(fields=['athlete', 'status']),
            models.Index(fields=['coach', 'status']),
        ]
    
    def __str__(self):
        if self.athlete:
            return f"Приглашение для {self.athlete.user.get_full_name()} на {self.event.title}"
        elif self.coach:
            return f"Приглашение для {self.coach.user.get_full_name()} на {self.event.title}"
        return f"Приглашение на {self.event.title}"