# apps/sports/models/sport.py
from django.db import models
from apps.core.models.base import TimeStampedModel

class Sport(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'sports_sport'
        verbose_name = 'Вид спорта'
        verbose_name_plural = 'Виды спорта'

    def __str__(self):
        return self.name