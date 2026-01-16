from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser
from apps.athletes.models.profile import AthleteProfile

class ParentChildLink(TimeStampedModel):
    parent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='children_links')
    child_profile = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE)
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('parent', 'child_profile')