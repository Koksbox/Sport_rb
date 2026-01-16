# apps/city_committee/models/managed_event.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .committee_staff import CommitteeStaff
from apps.events.models.event import Event

class ManagedEvent(TimeStampedModel):
    event = models.OneToOneField(Event, on_delete=models.CASCADE)
    managed_by = models.ForeignKey(CommitteeStaff, on_delete=models.CASCADE)

    class Meta:
        db_table = 'city_committee_managedevent'