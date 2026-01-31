# apps/achievements/models/achievement.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.athletes.models.profile import AthleteProfile
from apps.events.models.event import Event

ACHIEVEMENT_TYPE_CHOICES = [
    ('competition', 'Соревнование'),
    ('gto', 'ГТО'),
    ('certificate', 'Сертификат'),
    ('medal', 'Медаль'),
    ('diploma', 'Грамота'),
]

class Achievement(TimeStampedModel):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=255)
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='achievements/photos/', null=True, blank=True, help_text='Фото грамоты, медали и т.д. (обязательно)')

    class Meta:
        db_table = 'achievements_achievement'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title} - {self.athlete.user.get_full_name()}"