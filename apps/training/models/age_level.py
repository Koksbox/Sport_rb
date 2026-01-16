# apps/training/models/age_level.py
from django.db import models
from apps.core.models.base import TimeStampedModel

class AgeLevel(TimeStampedModel):
    name = models.CharField(max_length=50)  # "6–8 лет", "9–11 лет"
    min_age = models.PositiveSmallIntegerField()
    max_age = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'training_agelevel'
        ordering = ['min_age']

    def __str__(self):
        return self.name