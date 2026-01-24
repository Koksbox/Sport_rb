# apps/core/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.users.models import UserRole

User = get_user_model()

@receiver(post_migrate)
def create_main_admin(sender, **kwargs):
    """Автоматическое создание главного администратора после миграций"""
    # Проверяем, что это приложение core
    if sender.name != 'apps.core':
        return
    
    ADMIN_EMAIL = 'admin@admin.ru'
    ADMIN_PASSWORD = 'qwqwqw12'
    ADMIN_FIRST_NAME = 'Главный'
    ADMIN_LAST_NAME = 'Администратор'
    
    # Проверяем, существует ли уже главный администратор
    if not User.objects.filter(email=ADMIN_EMAIL).exists():
        # Создаём главного администратора
        admin = User.objects.create_user(
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            first_name=ADMIN_FIRST_NAME,
            last_name=ADMIN_LAST_NAME,
            is_staff=True,
            is_superuser=True,
        )
        
        # Создаём роль admin_rb
        UserRole.objects.create(
            user=admin,
            role='admin_rb',
            is_active=True
        )
    else:
        # Обновляем пароль и права, если администратор уже существует
        admin = User.objects.get(email=ADMIN_EMAIL)
        admin.set_password(ADMIN_PASSWORD)
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        
        # Создаём роль admin_rb, если её нет
        UserRole.objects.get_or_create(
            user=admin,
            role='admin_rb',
            defaults={'is_active': True}
        )
