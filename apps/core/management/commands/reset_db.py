# apps/core/management/commands/reset_db.py
"""
Команда для очистки базы данных и загрузки тестовых данных (без пользователей)
Использование: python manage.py reset_db
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import sys

class Command(BaseCommand):
    help = 'Очищает базу данных и загружает тестовые данные (без пользователей)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Пропустить выполнение миграций',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('⚠️  ВНИМАНИЕ: Это действие удалит все данные из базы данных (кроме главного администратора)!'))
        
        if not options.get('skip_migrations'):
            confirm = input('Вы уверены? Введите "yes" для продолжения: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Операция отменена.'))
                return
        
        try:
            with transaction.atomic():
                self.stdout.write(self.style.SUCCESS('Начинаем очистку базы данных...'))
                self.clear_all_data()
                
                self.stdout.write(self.style.SUCCESS('Загружаем тестовые данные...'))
                self.load_test_data()
                
                self.stdout.write(self.style.SUCCESS('✓ База данных успешно очищена и заполнена тестовыми данными!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))
            import traceback
            traceback.print_exc()

    def clear_all_data(self):
        """Очистка всех данных из базы"""
        from apps.organizations.models import Organization
        from apps.sports.models import Sport
        from apps.geography.models import City, Region, District
        from apps.events.models import Event, EventCategory, EventAgeGroup
        from apps.achievements.models import Achievement
        from apps.notifications.models import Notification
        from apps.audit.models import AuditLog
        from apps.files.models import FileUpload
        
        # Удаляем в правильном порядке (сначала зависимые, потом основные)
        self.stdout.write('  Удаление файлов...')
        FileUpload.objects.all().delete()
        
        self.stdout.write('  Удаление уведомлений...')
        Notification.objects.all().delete()
        
        self.stdout.write('  Удаление аудит-логов...')
        AuditLog.objects.all().delete()
        
        self.stdout.write('  Удаление достижений...')
        Achievement.objects.all().delete()
        
        self.stdout.write('  Удаление мероприятий...')
        Event.objects.all().delete()
        EventCategory.objects.all().delete()
        EventAgeGroup.objects.all().delete()
        
        self.stdout.write('  Удаление организаций...')
        SportDirection.objects.all().delete()
        Organization.objects.all().delete()
        
        self.stdout.write('  Удаление видов спорта...')
        Sport.objects.all().delete()
        
        self.stdout.write('  Удаление городов и районов...')
        District.objects.all().delete()
        City.objects.all().delete()
        Region.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('  ✓ Все данные удалены'))

    def load_test_data(self):
        """Загрузка тестовых данных (без пользователей)"""
        from apps.geography.models import Region, City
        from apps.sports.models import Sport
        from apps.events.models import EventCategory, EventAgeGroup, Event
        
        # 1. Регионы и города
        self.stdout.write('  Создание регионов и городов...')
        region, _ = Region.objects.get_or_create(name="Республика Башкортостан")
        
        cities_data = [
            ('Уфа', 'city'),
            ('Стерлитамак', 'city'),
            ('Салават', 'city'),
            ('Нефтекамск', 'city'),
            ('Октябрьский', 'city'),
            ('Туймазы', 'city'),
            ('Белебей', 'city'),
            ('Ишимбай', 'city'),
            ('Кумертау', 'city'),
            ('Сибай', 'city'),
            ('Булгаково', 'village'),
            ('Ивановка', 'hamlet'),
            ('Красный Яр', 'village'),
            ('Николаевка', 'village'),
        ]
        
        for city_name, settlement_type in cities_data:
            City.objects.get_or_create(
                name=city_name,
                region=region,
                defaults={'settlement_type': settlement_type}
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Создано {len(cities_data)} населенных пунктов'))
        
        # 2. Виды спорта
        self.stdout.write('  Создание видов спорта...')
        sports_data = [
            'Футбол',
            'Баскетбол',
            'Волейбол',
            'Хоккей',
            'Плавание',
            'Легкая атлетика',
            'Борьба',
            'Дзюдо',
            'Бокс',
            'Теннис',
            'Гимнастика',
            'Лыжный спорт',
            'Биатлон',
            'Шахматы',
            'Шашки',
        ]
        
        for sport_name in sports_data:
            Sport.objects.get_or_create(name=sport_name)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Создано {len(sports_data)} видов спорта'))
        
        # 3. Категории мероприятий
        self.stdout.write('  Создание категорий мероприятий...')
        categories = [
            ('competition', 'Соревнование'),
            ('marathon', 'Марафон'),
            ('gto_festival', 'Фестиваль ГТО'),
        ]
        
        for cat_code, cat_desc in categories:
            EventCategory.objects.get_or_create(
                name=cat_code,
                defaults={'description': cat_desc}
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Создано {len(categories)} категорий'))
        
        # 4. Примеры мероприятий
        self.stdout.write('  Создание мероприятий...')
        ufa_city = City.objects.filter(name='Уфа').first()
        
        if ufa_city:
            events_data = [
                {
                    'title': 'Чемпионат Республики Башкортостан по футболу',
                    'description': 'Ежегодный чемпионат среди юношеских команд',
                    'event_type': 'competition',
                    'level': 'republic',
                    'city': ufa_city,
                    'venue': 'г. Уфа, стадион "Динамо"',
                    'start_date': timezone.now() + timedelta(days=30),
                    'end_date': timezone.now() + timedelta(days=32),
                    'status': 'published',
                },
                {
                    'title': 'Кубок города по баскетболу',
                    'description': 'Турнир среди школьных команд',
                    'event_type': 'competition',
                    'level': 'city',
                    'city': ufa_city,
                    'venue': 'г. Уфа, ДС "Уфа-Арена"',
                    'start_date': timezone.now() + timedelta(days=45),
                    'end_date': timezone.now() + timedelta(days=47),
                    'status': 'published',
                },
                {
                    'title': 'Первенство по плаванию',
                    'description': 'Соревнования по плаванию среди детей',
                    'event_type': 'competition',
                    'level': 'city',
                    'city': ufa_city,
                    'venue': 'г. Уфа, бассейн "Олимпийский"',
                    'start_date': timezone.now() + timedelta(days=60),
                    'end_date': timezone.now() + timedelta(days=61),
                    'status': 'published',
                },
            ]
            
            for event_data in events_data:
                event, created = Event.objects.get_or_create(
                    title=event_data['title'],
                    defaults=event_data
                )
                
                # Добавляем возрастные группы к мероприятию
                if created:
                    age_groups_data = [
                        (6, 10),
                        (11, 14),
                        (15, 17),
                    ]
                    for min_age, max_age in age_groups_data:
                        EventAgeGroup.objects.create(
                            event=event,
                            min_age=min_age,
                            max_age=max_age
                        )
            
            self.stdout.write(self.style.SUCCESS(f'  ✓ Создано {len(events_data)} мероприятий'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Тестовые данные успешно загружены!'))
