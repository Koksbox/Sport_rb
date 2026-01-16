from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser
from apps.sports.models import Sport

HEALTH_GROUP_CHOICES = [('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV')]

class AthleteProfile(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='athletes/photos/', blank=True)
    school_or_university = models.CharField(max_length=255, blank=True)
    main_sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, related_name='main_athletes')
    additional_sports = models.ManyToManyField(Sport, blank=True, related_name='secondary_athletes')
    health_group = models.CharField(max_length=2, choices=HEALTH_GROUP_CHOICES, blank=True)
    goals = models.JSONField(default=list)  # ["ЗОЖ", "Соревнования", "ГТО"]