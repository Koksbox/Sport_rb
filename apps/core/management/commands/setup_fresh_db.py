# apps/core/management/commands/setup_fresh_db.py
"""
Команда для полной настройки свежей базы данных:
1. Очистка всех данных
2. Загрузка базовых данных (регионы, города, виды спорта)
3. Создание тестового пользователя
Использование: python manage.py setup_fresh_db
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = 'Полная настройка свежей базы данных: очистка + базовые данные + тестовый пользователь'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Пропустить подтверждение',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('⚠️  ВНИМАНИЕ: Это действие удалит ВСЕ данные из базы данных!'))
        
        if not options.get('force'):
            confirm = input('Вы уверены? Введите "yes" для продолжения: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Операция отменена.'))
                return
        
        try:
            # 1. Применение миграций (если есть новые)
            self.stdout.write(self.style.SUCCESS('\n1. Применение миграций...'))
            call_command('migrate', verbosity=1)
            
            with transaction.atomic():
                # 2. Очистка всех данных
                self.stdout.write(self.style.SUCCESS('\n2. Очистка базы данных...'))
                call_command('reset_all_data', '--force')
                
                # 3. Загрузка базовых данных
                self.stdout.write(self.style.SUCCESS('\n3. Загрузка базовых данных...'))
                call_command('reset_db', '--skip-migrations')
                
                # 4. Создание главного администратора (если нужно)
                self.stdout.write(self.style.SUCCESS('\n4. Проверка главного администратора...'))
                call_command('create_main_admin')
                
                # 5. Создание тестового пользователя
                self.stdout.write(self.style.SUCCESS('\n5. Создание тестового пользователя...'))
                call_command('create_test_user')
                
                self.stdout.write(self.style.SUCCESS('\n✓ База данных полностью настроена!'))
                self.stdout.write(self.style.SUCCESS('\nДоступные аккаунты:'))
                self.stdout.write(self.style.SUCCESS('  - Главный администратор: admin@admin.ru / qwqwqw12'))
                self.stdout.write(self.style.SUCCESS('  - Тестовый пользователь: edgarvaliev463@xmail.com / qwqwqw12'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))
            import traceback
            traceback.print_exc()
