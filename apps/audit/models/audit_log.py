# apps/audit/models/audit_log.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

ACTION_CHOICES = [
    ('login', 'Вход'),
    ('role_assigned', 'Назначена роль'),
    ('org_verified', 'Организация подтверждена'),
    ('data_export', 'Экспорт данных'),
    ('2fa_enabled', 'Включена 2FA'),
]

class AuditLog(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict)

    class Meta:
        db_table = 'audit_auditlog'
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['created_at']),
        ]