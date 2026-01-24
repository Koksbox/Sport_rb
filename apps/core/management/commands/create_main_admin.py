# apps/core/management/commands/create_main_admin.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import UserRole
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Создаёт главного администратора системы'

    def handle(self, *args, **options):
        # Данные главного администратора
        ADMIN_EMAIL = 'admin@admin.ru'
        ADMIN_PASSWORD = 'qwqwqw12'
        ADMIN_FIRST_NAME = 'Главный'
        ADMIN_LAST_NAME = 'Администратор'
        
        # Проверяем, существует ли уже главный администратор
        if User.objects.filter(email=ADMIN_EMAIL).exists():
            admin = User.objects.get(email=ADMIN_EMAIL)
            self.stdout.write(self.style.WARNING(f'Главный администратор уже существует: {admin.email}'))
            
            # Обновляем пароль на случай, если он был изменён
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
            
            self.stdout.write(self.style.SUCCESS('Пароль главного администратора обновлён'))
        else:
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
            
            self.stdout.write(self.style.SUCCESS(f'Главный администратор создан: {admin.email}'))
        
        self.stdout.write(self.style.SUCCESS(f'Пароль: {ADMIN_PASSWORD}'))
        self.stdout.write(self.style.WARNING('ВАЖНО: Измените пароль после первого входа!'))
