# apps/organizations/models/organization_role_request.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

REQUEST_STATUS_CHOICES = [
    ('pending', 'Ожидает рассмотрения'),
    ('approved', 'Одобрено'),
    ('rejected', 'Отклонено'),
]

class OrganizationRoleRequest(TimeStampedModel):
    """Заявка на получение роли организации"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='organization_role_requests')
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text='Дополнительная информация от пользователя')
    reviewed_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_organization_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text='Причина отклонения заявки')
    
    class Meta:
        db_table = 'organizations_organizationrolerequest'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заявка на роль организации от {self.user.get_full_name()} ({self.status})"
