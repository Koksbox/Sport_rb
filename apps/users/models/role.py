# apps/users/models/role.py
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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'users_userrole'
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user} → {self.role}"