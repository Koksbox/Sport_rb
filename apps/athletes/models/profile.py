# apps/athletes/models/profile.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser
from apps.sports.models.sport import Sport
from apps.geography.models.city import City

HEALTH_GROUP_CHOICES = [
    ('I', 'I'),
    ('II', 'II'),
    ('III', 'III'),
    ('IV', 'IV'),
]

class AthleteProfile(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='athlete_profile')
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    school_or_university = models.CharField(max_length=255, blank=True)
    main_sport = models.ForeignKey(Sport, on_delete=models.PROTECT, related_name='main_athletes')
    health_group = models.CharField(max_length=3, choices=HEALTH_GROUP_CHOICES, blank=True)
    goals = models.JSONField(default=list)  # ["ЗОЖ", "Соревнования", "ГТО"]

    class Meta:
        db_table = 'athletes_profile'