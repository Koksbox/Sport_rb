# apps/admin_rb/models/system_role.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

SYSTEM_ROLE_CHOICES = [
    ('superadmin', 'Суперадмин РБ'),
    ('moderator', 'Модератор организаций'),
]

class SystemRoleAssignment(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='system_role')
    role = models.CharField(max_length=20, choices=SYSTEM_ROLE_CHOICES)

    class Meta:
        db_table = 'admin_rb_systemrole'