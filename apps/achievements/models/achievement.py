# apps/achievements/models/achievement.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.athletes.models.profile import AthleteProfile
from apps.events.models.event import Event

ACHIEVEMENT_TYPE_CHOICES = [
    ('competition', 'Соревнование'),
    ('gto', 'ГТО'),
    ('certificate', 'Сертификат'),
]

class Achievement(TimeStampedModel):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=255)
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    description = models.TextField(blank=True)
    proof_file = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'achievements_achievement'
        ordering = ['-date']