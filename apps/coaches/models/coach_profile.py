# apps/coaches/models/coach_profile.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser
from apps.sports.models.sport import Sport
from apps.geography.models.city import City

class CoachProfile(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='coach_profile')
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    phone = models.CharField(max_length=15, blank=True)
    telegram = models.CharField(max_length=100, blank=True)
    specialization = models.ForeignKey(Sport, on_delete=models.PROTECT)
    experience_years = models.PositiveSmallIntegerField()
    education = models.TextField(blank=True)

    class Meta:
        db_table = 'coaches_coachprofile'