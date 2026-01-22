# apps/users/models/role.py
import uuid
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
    unique_id = models.CharField(max_length=12, unique=True, db_index=True, editable=False, null=True, blank=True)
    
    class Meta:
        db_table = 'users_userrole'
        unique_together = ('user', 'role')
    
    def save(self, *args, **kwargs):
        if not self.unique_id:
            # Генерируем уникальный ID из 8 символов (цифры и буквы)
            import random
            import string
            while True:
                self.unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not UserRole.objects.filter(unique_id=self.unique_id).exists():
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} → {self.role} (ID: {self.unique_id})"