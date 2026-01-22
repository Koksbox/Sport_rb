# apps/organizations/models/documents.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from .organization import Organization

DOCUMENT_TYPE_CHOICES = [
    ('inn', 'ИНН'),
    ('license', 'Лицензия'),
    ('charter', 'Устав'),
    ('other', 'Другое'),
]

class OrganizationDocument(TimeStampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file_path = models.CharField(max_length=500)  # путь в MinIO/S3

    class Meta:
        db_table = 'organizations_document'