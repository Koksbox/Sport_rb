# apps/achievements/models/gto_result.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.athletes.models.profile import AthleteProfile

GTO_LEVEL_CHOICES = [
    ('1', 'Ступень 1 (6–8 лет)'),
    ('2', 'Ступень 2 (9–10 лет)'),
    ('3', 'Ступень 3 (11–12 лет)'),
    ('4', 'Ступень 4 (13–15 лет)'),
    ('5', 'Ступень 5 (16–17 лет)'),
    ('6', 'Ступень 6 (18–29 лет)'),
    ('7', 'Ступень 7 (30–39 лет)'),
]

GTO_BADGE_CHOICES = [
    ('bronze', 'Бронзовый'),
    ('silver', 'Серебряный'),
    ('gold', 'Золотой'),
]

class GtoResult(TimeStampedModel):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='gto_results')
    level = models.CharField(max_length=10, choices=GTO_LEVEL_CHOICES)
    badge = models.CharField(max_length=10, choices=GTO_BADGE_CHOICES)
    completion_date = models.DateField()
    protocol_number = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'achievements_gtoresult'