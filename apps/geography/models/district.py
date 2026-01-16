from django.db import models
from apps.core.models.base import TimeStampedModel
from .city import City

class District(TimeStampedModel):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)