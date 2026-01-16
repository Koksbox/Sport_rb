# apps/organizations/models/priority.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .organization import Organization
from apps.city_committee.models.committee_staff import CommitteeStaff

class PriorityAssignment(TimeStampedModel):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='priority')
    assigned_by = models.ForeignKey(CommitteeStaff, on_delete=models.PROTECT)
    reason = models.TextField(blank=True)

    class Meta:
        db_table = 'organizations_priority'