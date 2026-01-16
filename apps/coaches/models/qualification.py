# apps/coaches/models/qualification.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .coach_profile import CoachProfile

class Qualification(TimeStampedModel):
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, related_name='qualifications')
    title = models.CharField(max_length=255)  # "Мастер спорта", "Тренер высшей категории"
    issued_by = models.CharField(max_length=255)
    issue_date = models.DateField()
    file_path = models.CharField(max_length=500, blank=True)  # сертификат

    class Meta:
        db_table = 'coaches_qualification'