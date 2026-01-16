# apps/city_committee/models/city_permission.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .committee_staff import CommitteeStaff
from apps.organizations.models.organization import Organization

class CityPermission(TimeStampedModel):
    staff = models.ForeignKey(CommitteeStaff, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    can_manage = models.BooleanField(default=False)  # например, право рекомендовать

    class Meta:
        db_table = 'city_committee_citypermission'
        unique_together = ('staff', 'organization')