# apps/parents/models/parent_profile.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

class ParentProfile(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='parent_profile')

    class Meta:
        db_table = 'parents_parentprofile'