# apps/notifications/models/subscription.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

SUBSCRIPTION_TYPE_CHOICES = [
    ('event_updates', 'Обновления мероприятий'),
    ('attendance_alerts', 'Пропуски тренировок'),
    ('achievements', 'Достижения ребёнка'),
]

class NotificationSubscription(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notification_subscriptions')
    subscription_type = models.CharField(max_length=50, choices=SUBSCRIPTION_TYPE_CHOICES)
    enabled = models.BooleanField(default=True)

    class Meta:
        db_table = 'notifications_subscription'
        unique_together = ('user', 'subscription_type')