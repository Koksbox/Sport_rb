# apps/events/models/event.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.geography.models.city import City
from apps.organizations.models.organization import Organization
from apps.users.models.user import CustomUser

EVENT_TYPE_CHOICES = [
    ('competition', 'Соревнование'),
    ('marathon', 'Марафон'),
    ('gto_festival', 'Фестиваль ГТО'),
    ('open_doors', 'Дни открытых дверей'),
    ('camp', 'Спортивный лагерь'),
]

EVENT_LEVEL_CHOICES = [
    ('school', 'Школьный'),
    ('district', 'Районный'),
    ('city', 'Городской'),
    ('republic', 'Республиканский'),
    ('national', 'Всероссийский'),
]

EVENT_STATUS_CHOICES = [
    ('draft', 'Черновик'),
    ('published', 'Опубликовано'),
    ('completed', 'Завершено'),
    ('cancelled', 'Отменено'),
]

class Event(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    level = models.CharField(max_length=20, choices=EVENT_LEVEL_CHOICES)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    venue = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    organizer_org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    organizer_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    requires_registration = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='draft')

    class Meta:
        db_table = 'events_event'
        ordering = ['-start_date']