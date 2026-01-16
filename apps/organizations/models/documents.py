from django.db import models
from apps.core.models.base import TimeStampedModel
from .organization import Organization
from apps.files.models.file import StoredFile

class OrganizationDocument(TimeStampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    file = models.ForeignKey(StoredFile, on_delete=models.CASCADE)
    doc_type = models.CharField(max_length=50)  # 'license', 'charter', 'inn_copy'