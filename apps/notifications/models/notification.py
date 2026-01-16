from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

NOTIFICATION_TYPES = [
    ('medical_review', 'Ознакомьтесь с мед. данными'),
    ('child_linked', 'Подтверждение связи с ребёнком'),
    ('event_registered', 'Регистрация на мероприятие'),
    ('attendance_missed', 'Пропуск тренировки'),
]

class Notification(TimeStampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_via = models.CharField(max_length=20)  # 'telegram', 'email', 'system'
    related_object_id = models.PositiveIntegerField(null=True, blank=True)