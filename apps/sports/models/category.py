# apps/sports/models/category.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .sport import Sport

class SportCategory(TimeStampedModel):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)  # Например: "Лёгкая атлетика", "Плавание"

    class Meta:
        db_table = 'sports_category'
        unique_together = ('sport', 'name')

    def __str__(self):
        return f"{self.sport.name} – {self.name}"