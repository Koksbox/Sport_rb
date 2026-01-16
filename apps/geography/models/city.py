# apps/geography/models/city.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .region import Region

class City(TimeStampedModel):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name='cities')

    class Meta:
        db_table = 'geography_city'
        unique_together = ('name', 'region')

    def __str__(self):
        return f"{self.name}, {self.region.name}"