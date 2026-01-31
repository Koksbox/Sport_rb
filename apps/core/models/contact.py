# apps/core/models/contact.py
from django.db import models
from apps.core.models.base import TimeStampedModel
from apps.users.models.user import CustomUser

CONTACT_SUBJECT_CHOICES = [
    ('technical', 'Техническая проблема'),
    ('question', 'Вопрос по использованию'),
    ('suggestion', 'Предложение по улучшению'),
    ('registration', 'Проблема с регистрацией'),
    ('other', 'Другое'),
]

CONTACT_STATUS_CHOICES = [
    ('new', 'Новое'),
    ('in_progress', 'В обработке'),
    ('resolved', 'Решено'),
    ('closed', 'Закрыто'),
]

class ContactMessage(TimeStampedModel):
    """Сообщения обратной связи от пользователей"""
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_messages')
    name = models.CharField(max_length=255, help_text="Имя отправителя")
    email = models.EmailField(help_text="Email отправителя")
    phone = models.CharField(max_length=20, blank=True, help_text="Телефон отправителя")
    subject = models.CharField(max_length=50, choices=CONTACT_SUBJECT_CHOICES, help_text="Тема обращения")
    message = models.TextField(help_text="Текст сообщения")
    role_id = models.CharField(max_length=20, blank=True, help_text="ID роли, с которой отправлено обращение")
    status = models.CharField(max_length=20, choices=CONTACT_STATUS_CHOICES, default='new', db_index=True)
    admin_response = models.TextField(blank=True, help_text="Ответ администрации")
    responded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='responded_contacts')
    responded_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'core_contactmessage'
        verbose_name = 'Сообщение обратной связи'
        verbose_name_plural = 'Сообщения обратной связи'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()} ({self.created_at.strftime('%d.%m.%Y')})"
