from django.db import models
from apps.core.models.base import TimeStampedModel

class Sport(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name