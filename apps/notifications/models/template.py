# apps/notifications/models/template.py
from django.db import models
from apps.core.models.base import TimeStampedModel

NOTIFICATION_CHANNEL_CHOICES = [
    ('email', 'Email'),
    ('telegram', 'Telegram'),
    ('system', 'Системное'),
]

class NotificationTemplate(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)  # Например: "medical_review", "enrollment_approved"
    channel = models.CharField(max_length=20, choices=NOTIFICATION_CHANNEL_CHOICES)
    subject_template = models.CharField(max_length=255, blank=True)  # для email / telegram заголовок
    body_template = models.TextField()  # шаблон тела с плейсхолдерами: {{ user.first_name }}, {{ event.title }} и т.д.
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'notifications_template'
        verbose_name = 'Шаблон уведомления'
        verbose_name_plural = 'Шаблоны уведомлений'

    def __str__(self):
        return f"{self.name} ({self.get_channel_display()})"