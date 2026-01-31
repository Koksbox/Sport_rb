# apps/city_committee/models/committee_registration.py
from django.db import models
from apps.core.models.base import TimeStampedModel

class CommitteeRegistrationCode(TimeStampedModel):
    """Коды регистрации для сотрудников спорткомитета"""
    code = models.CharField(max_length=50, unique=True, db_index=True, help_text="Уникальный код регистрации")
    city_name = models.CharField(max_length=100, help_text="Город, для которого выдан код")
    department = models.CharField(max_length=255, blank=True, help_text="Отдел/подразделение")
    position = models.CharField(max_length=255, blank=True, help_text="Должность")
    issued_by = models.CharField(max_length=255, blank=True, help_text="Кем выдан код")
    is_used = models.BooleanField(default=False, db_index=True)
    used_by_email = models.EmailField(null=True, blank=True, help_text="Email пользователя, использовавшего код")
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Срок действия кода")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'city_committee_registrationcode'
        verbose_name = 'Код регистрации спорткомитета'
        verbose_name_plural = 'Коды регистрации спорткомитета'

    def __str__(self):
        return f"{self.code} - {self.city_name} ({'использован' if self.is_used else 'активен'})"
