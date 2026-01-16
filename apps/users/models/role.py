from django.db import models
from apps.core.models.base import TimeStampedModel
from .user import CustomUser

ROLE_CHOICES = [
    ('athlete', 'Спортсмен'),
    ('parent', 'Родитель'),
    ('coach', 'Тренер'),
    ('director', 'Директор'),
    ('committee_staff', 'Сотрудник горкомспорта'),
    ('admin_rb', 'Админ РБ'),
]

class UserRole(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'role')