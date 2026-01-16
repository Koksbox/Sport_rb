# apps/athletes/models/profile.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser
from apps.sports.models import Sport

HEALTH_GROUP_CHOICES = [('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV')]

class AthleteProfile(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='athlete_profile')
    photo = models.ImageField(upload_to='athletes/photos/', blank=True, null=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=[('male', 'Мужской'), ('female', 'Женский')])
    city = models.ForeignKey('geography.City', on_delete=models.SET_NULL, null=True, blank=True)
    school = models.CharField(max_length=255, blank=True)
    main_sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, related_name='main_athletes')
    health_group = models.CharField(max_length=10, choices=HEALTH_GROUP_CHOICES, blank=True)
    goals = models.JSONField(default=list)  # ["gto", "competitions", "zozh"]

    def __str__(self):
        return f"{self.user.get_full_name()} (спортсмен)"