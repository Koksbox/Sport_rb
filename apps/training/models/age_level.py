from django.db import models
from apps.core.models.base import TimeStampedModel

class AgeLevel(TimeStampedModel):
    name = models.CharField(max_length=50)  # "6–8 лет"
    min_age = models.PositiveSmallIntegerField()
    max_age = models.PositiveSmallIntegerField()