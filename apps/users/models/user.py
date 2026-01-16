from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from apps.core.models.base import TimeStampedModel, SoftDeleteModel
from apps.geography.models import City

GENDER_CHOICES = [('M', 'Мужской'), ('F', 'Женский')]

class CustomUser(AbstractBaseUser, PermissionsMixin, TimeStampedModel, SoftDeleteModel):
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"