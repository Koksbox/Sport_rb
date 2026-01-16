from django.db import models
from apps.core.models.base import TimeStampedModel

class Region(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)  # "02" — Башкортостан

    def __str__(self):
        return self.name