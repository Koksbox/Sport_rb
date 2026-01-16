from django.db import models
from apps.users.models.user import CustomUser

PROVIDER_CHOICES = [
    ('email', 'Email'),
    ('vk', 'VKontakte'),
    ('telegram', 'Telegram'),
]

class AuthProvider(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='auth_providers')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    external_id = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'provider')