from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

class StoredFile(TimeStampedModel):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    mime_type = models.CharField(max_length=100)
    size_bytes = models.PositiveBigIntegerField()
    purpose = models.CharField(max_length=100)  # 'license', 'medical', 'certificate'