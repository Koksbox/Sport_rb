from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser
from apps.sports.models import Sport

class CoachProfile(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='coaches/photos/', blank=True)
    experience_years = models.PositiveSmallIntegerField()
    specialization = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True)
    telegram = models.CharField(max_length=100, blank=True)