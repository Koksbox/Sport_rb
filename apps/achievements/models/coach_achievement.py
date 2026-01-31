# apps/achievements/models/coach_achievement.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.coaches.models.coach_profile import CoachProfile
from apps.events.models.event import Event

COACH_ACHIEVEMENT_TYPE_CHOICES = [
    ('certificate', 'Сертификат'),
    ('diploma', 'Диплом'),
    ('award', 'Награда'),
    ('qualification', 'Квалификация'),
    ('competition_result', 'Результат соревнования'),
]

class CoachAchievement(TimeStampedModel):
    """Достижения и сертификаты тренеров"""
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=255, help_text='Название достижения или сертификата')
    achievement_type = models.CharField(max_length=20, choices=COACH_ACHIEVEMENT_TYPE_CHOICES)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, help_text='Связанное мероприятие (если есть)')
    date = models.DateField(help_text='Дата получения')
    description = models.TextField(blank=True, help_text='Описание достижения')
    photo = models.ImageField(upload_to='coaches/achievements/photos/', null=True, blank=True, help_text='Фото сертификата, грамоты и т.д. (обязательно)')
    issued_by = models.CharField(max_length=255, blank=True, help_text='Кем выдано')

    class Meta:
        db_table = 'achievements_coachachievement'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title} - {self.coach.user.get_full_name()}"
