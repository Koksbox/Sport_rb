# apps/notifications/models/notification.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

NOTIFICATION_TYPE_CHOICES = [
    ('medical_review', 'Ознакомьтесь с мед. данными'),
    ('enrollment_approved', 'Зачисление одобрено'),
    ('event_result', 'Результаты соревнований'),
    ('mass_notification', 'Массовое уведомление'),
]

class Notification(TimeStampedModel):
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    related_object_id = models.PositiveBigIntegerField(null=True, blank=True)  # Generic FK если нужно

    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']