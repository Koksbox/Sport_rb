# apps/city_committee/models/committee_staff.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser
from apps.geography.models.city import City

class CommitteeStaff(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='committee_role')
    city = models.ForeignKey(City, on_delete=models.PROTECT)

    class Meta:
        db_table = 'city_committee_committeestaff'