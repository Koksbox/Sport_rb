from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser
from apps.geography.models import City

class CommitteeStaff(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)