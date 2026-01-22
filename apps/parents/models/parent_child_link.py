# apps/parents/models/parent_child_link.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser
from apps.athletes.models.profile import AthleteProfile

LINK_STATUS_CHOICES = [
    ('pending_parent', 'Ожидает подтверждения от родителя'),
    ('pending_child', 'Ожидает подтверждения от ребёнка'),
    ('confirmed', 'Подтверждено'),
    ('rejected', 'Отклонено'),
]

class ParentChildLink(TimeStampedModel):
    parent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='children_links')
    child_profile = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='parent_links')
    status = models.CharField(max_length=20, choices=LINK_STATUS_CHOICES, default='pending_child')
    requested_by = models.CharField(max_length=20, choices=[('parent', 'Родитель'), ('child', 'Ребёнок')], default='parent')
    is_confirmed = models.BooleanField(default=False)  # Оставляем для обратной совместимости

    class Meta:
        db_table = 'parents_parentchildlink'
        unique_together = ('parent', 'child_profile')
    
    def save(self, *args, **kwargs):
        # Синхронизируем is_confirmed со status
        self.is_confirmed = (self.status == 'confirmed')
        super().save(*args, **kwargs)