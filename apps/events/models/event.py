from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.geography.models import City
from apps.users.models.user import CustomUser
from apps.organizations.models.organization import Organization

EVENT_TYPE_CHOICES = [
    ('competition', 'Соревнование'),
    ('marathon', 'Марафон'),
    ('gto_festival', 'Фестиваль ГТО'),
    ('open_day', 'День открытых дверей'),
    ('camp', 'Спортивный лагерь'),
]

EVENT_LEVEL_CHOICES = [
    ('school', 'Школьный'),
    ('district', 'Районный'),
    ('city', 'Городской'),
    ('republic', 'Республиканский'),
    ('russia', 'Всероссийский'),
]

class Event(TimeStampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    level = models.CharField(max_length=20, choices=EVENT_LEVEL_CHOICES)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    venue = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    organizer_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    organizer_org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)
    requires_registration = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)