from django.db import models
from apps.core.models.base import TimeStampedModel
from .region import Region

class City(TimeStampedModel):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    oktmo_code = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('name', 'region')