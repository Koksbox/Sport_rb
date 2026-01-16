# apps/events/models/category.py
from django.db import models
from apps.core.models.base import TimeStampedModel

EVENT_CATEGORY_CHOICES = [
    ('competition', 'Соревнование'),
    ('marathon', 'Марафон'),
    ('gto_festival', 'Фестиваль ГТО'),
    ('open_doors', 'Дни открытых дверей'),
    ('camp', 'Спортивный лагерь'),
]

class EventCategory(TimeStampedModel):
    name = models.CharField(max_length=50, choices=EVENT_CATEGORY_CHOICES, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'events_category'

    def __str__(self):
        return self.get_name_display()