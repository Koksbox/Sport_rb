# apps/files/models/file.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

FILE_CATEGORY_CHOICES = [
    ('document', 'Документ'),
    ('certificate', 'Сертификат'),
    ('photo', 'Фото'),
    ('other', 'Другое'),
]

class StoredFile(TimeStampedModel):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    original_name = models.CharField(max_length=255)
    stored_path = models.CharField(max_length=500)  # MinIO/S3 key
    category = models.CharField(max_length=20, choices=FILE_CATEGORY_CHOICES)
    size_bytes = models.PositiveBigIntegerField()
    mime_type = models.CharField(max_length=100)

    class Meta:
        db_table = 'files_file'