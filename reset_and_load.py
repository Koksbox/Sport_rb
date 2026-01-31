#!/usr/bin/env python
"""
Скрипт для очистки БД и загрузки пробных данных
"""
import os
import sys
import django

# Настройка Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from django.core.management import call_command
from django.db import transaction

def main():
    print("=" * 60)
    print("Очистка базы данных и загрузка пробных данных")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            # 1. Очистка всех данных
            print("\n1. Очистка базы данных...")
            call_command('reset_all_data', '--force')
            
            # 2. Применение миграций
            print("\n2. Применение миграций...")
            call_command('migrate', verbosity=1)
            
            # 3. Загрузка базовых данных
            print("\n3. Загрузка базовых данных...")
            call_command('reset_db', '--skip-migrations')
            
            # 4. Создание главного администратора (если нужно)
            print("\n4. Проверка главного администратора...")
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(is_superuser=True).exists():
                print("  Создание главного администратора...")
                User.objects.create_superuser(
                    email='admin@admin.ru',
                    password='qwqwqw12',
                    first_name='Админ',
                    last_name='Админов'
                )
                print("  ✓ Главный администратор создан (admin@admin.ru / qwqwqw12)")
            else:
                print("  ✓ Главный администратор уже существует")
            
            # 5. Создание тестового пользователя
            print("\n5. Создание тестового пользователя...")
            call_command('create_test_user')
            
            print("\n" + "=" * 60)
            print("✓ База данных полностью настроена!")
            print("=" * 60)
            print("\nДоступные аккаунты:")
            print("  - Главный администратор: admin@admin.ru / qwqwqw12")
            print("  - Тестовый пользователь: edgarvaliev463@xmail.com / qwqwqw12")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
