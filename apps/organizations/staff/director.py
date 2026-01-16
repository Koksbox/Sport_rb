# apps/organizations/staff/director.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser
from ..models.organization import Organization

class Director(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='director_role')
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='director')

    class Meta:
        db_table = 'organizations_director'