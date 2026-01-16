# apps/users/models/deletion_request.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .user import CustomUser

class DeletionRequest(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    reason = models.TextField(blank=True)
    processed = models.BooleanField(default=False)

    class Meta:
        db_table = 'users_deletionrequest'