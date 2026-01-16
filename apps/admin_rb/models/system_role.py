from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

class SystemRoleAssignment(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=30)  # 'moderator', 'super_admin'
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='+')