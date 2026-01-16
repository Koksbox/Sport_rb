from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

class AuditLog(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)  # 'org_verified', 'user_deleted'
    ip_address = models.GenericIPAddressField(null=True)
    details = models.JSONField(default=dict)