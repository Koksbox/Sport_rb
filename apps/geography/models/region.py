# apps/geography/models/region.py
from django.db import models
from apps.core.models.base import TimeStampedModel

class Region(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'geography_region'
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'

    def __str__(self):
        return self.name