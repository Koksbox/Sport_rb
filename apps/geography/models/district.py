# apps/geography/models/district.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .city import City  # ← можно, потому что City не зависит от District

class District(TimeStampedModel):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='districts')

    class Meta:
        db_table = 'geography_district'
        unique_together = ('name', 'city')

    def __str__(self):
        return f"{self.name}, {self.city.name}"