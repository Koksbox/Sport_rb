from django.db import models
from apps.users.models.user import CustomUser
from ..models.organization import Organization

class Director(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    appointed_at = models.DateTimeField(auto_now_add=True)