# apps/authn/models/auth_provider.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

PROVIDER_CHOICES = [
    ('email', 'Email'),
    ('telegram', 'Telegram'),
    ('vk', 'VKontakte'),
]

class AuthProvider(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='auth_providers')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    external_id = models.CharField(max_length=255)  # telegram_id, vk_id, email

    class Meta:
        db_table = 'authn_authprovider'
        unique_together = ('provider', 'external_id')