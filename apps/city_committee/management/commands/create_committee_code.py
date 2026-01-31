# apps/city_committee/management/commands/create_committee_code.py
"""
Management команда для создания кодов регистрации сотрудников спорткомитета
Использование: python manage.py create_committee_code --city "Уфа" --count 5
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.city_committee.models import CommitteeRegistrationCode
import random
import string


class Command(BaseCommand):
    help = 'Создаёт коды регистрации для сотрудников спорткомитета'

    def add_arguments(self, parser):
        parser.add_argument(
            '--city',
            type=str,
            required=True,
            help='Название города (например: Уфа)',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Количество кодов для создания (по умолчанию: 1)',
        )
        parser.add_argument(
            '--department',
            type=str,
            default='',
            help='Отдел/подразделение',
        )
        parser.add_argument(
            '--position',
            type=str,
            default='',
            help='Должность',
        )
        parser.add_argument(
            '--issued-by',
            type=str,
            default='Администратор',
            help='Кем выдан код',
        )
        parser.add_argument(
            '--expires-days',
            type=int,
            default=None,
            help='Срок действия кода в днях (по умолчанию без срока)',
        )
        parser.add_argument(
            '--code-length',
            type=int,
            default=8,
            help='Длина кода (по умолчанию: 8 символов)',
        )

    def handle(self, *args, **options):
        city_name = options['city']
        count = options['count']
        department = options['department']
        position = options['position']
        issued_by = options['issued_by']
        expires_days = options['expires_days']
        code_length = options['code_length']
        
        self.stdout.write(self.style.SUCCESS(f'Создание {count} кодов для города "{city_name}"...'))
        
        created_codes = []
        for i in range(count):
            # Генерируем уникальный код
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=code_length))
                if not CommitteeRegistrationCode.objects.filter(code=code).exists():
                    break
            
            # Определяем срок действия
            expires_at = None
            if expires_days:
                expires_at = timezone.now() + timedelta(days=expires_days)
            
            # Создаём код
            reg_code = CommitteeRegistrationCode.objects.create(
                code=code,
                city_name=city_name,
                department=department,
                position=position,
                issued_by=issued_by,
                expires_at=expires_at,
                is_active=True,
                is_used=False
            )
            
            created_codes.append(reg_code)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создан код: {code}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Успешно создано {len(created_codes)} кодов регистрации!'))
        self.stdout.write(self.style.WARNING('\nКоды регистрации:'))
        for code in created_codes:
            self.stdout.write(f'  {code.code} - {code.city_name}')
        
        if expires_days:
            self.stdout.write(self.style.WARNING(f'\n⚠ Коды действительны {expires_days} дней'))
