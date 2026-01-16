from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.geography.models import City

class AnalyticsCache(TimeStampedModel):
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    metric = models.CharField(max_length=100)  # 'total_athletes', 'gto_passed', etc.
    value = models.JSONField()  # {'count': 123, 'by_age': {...}}
    refreshed_at = models.DateTimeField(auto_now=True)