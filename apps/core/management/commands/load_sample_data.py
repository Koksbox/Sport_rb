# apps/core/management/commands/load_sample_data.py
"""
Management команда для загрузки пробных данных в базу данных
Использование: python manage.py load_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Загружает пробные данные в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные перед загрузкой',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаем загрузку пробных данных...'))

        if options['clear']:
            self.stdout.write(self.style.WARNING('Очистка существующих данных...'))
            self.clear_data()

        # Загружаем данные
        self.create_regions_and_cities()
        self.create_sports()
        self.create_users()
        self.create_organizations()
        self.create_events()

        self.stdout.write(self.style.SUCCESS('✓ Пробные данные успешно загружены!'))

    def clear_data(self):
        """Очистка существующих данных (кроме суперпользователя)"""
        from apps.events.models import Event
        from apps.organizations.models import Organization
        from apps.athletes.models import AthleteProfile
        from apps.coaches.models import CoachProfile
        from apps.parents.models import ParentProfile
        from apps.users.models import UserRole
        from apps.geography.models import City, Region
        from apps.sports.models import Sport, SportCategory

        Event.objects.all().delete()
        Organization.objects.all().delete()
        AthleteProfile.objects.all().delete()
        CoachProfile.objects.all().delete()
        ParentProfile.objects.all().delete()
        UserRole.objects.exclude(user__is_superuser=True).delete()
        User.objects.filter(is_superuser=False).delete()
        Sport.objects.all().delete()
        SportCategory.objects.all().delete()
        City.objects.all().delete()
        Region.objects.all().delete()

    def create_regions_and_cities(self):
        """Создание регионов и городов"""
        self.stdout.write('Создание регионов и городов...')
        
        from apps.geography.models import Region, City

        region, _ = Region.objects.get_or_create(
            name='Республика Башкортостан'
        )

        cities_data = [
            'Уфа', 'Стерлитамак', 'Салават', 'Нефтекамск', 
            'Октябрьский', 'Туймазы', 'Белебей', 'Ишимбай',
            'Сибай', 'Кумертау', 'Мелеуз', 'Бирск'
        ]

        cities = []
        for city_name in cities_data:
            city, _ = City.objects.get_or_create(
                name=city_name,
                defaults={'region': region}
            )
            cities.append(city)

        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(cities)} городов'))

    def create_sports(self):
        """Создание видов спорта"""
        self.stdout.write('Создание видов спорта...')
        
        from apps.sports.models import SportCategory, Sport

        # Сначала создаем все виды спорта
        sports_data = [
            'Футбол', 'Баскетбол', 'Волейбол', 'Хоккей', 'Теннис',
            'Дзюдо', 'Карате', 'Бокс', 'Борьба', 'Тхэквондо',
            'Плавание', 'Водное поло', 'Прыжки в воду',
            'Бег', 'Прыжки', 'Метание', 'Многоборье',
            'Художественная гимнастика', 'Спортивная гимнастика',
            'Лыжи', 'Коньки', 'Биатлон'
        ]

        sports_count = 0
        created_sports = {}
        
        for sport_name in sports_data:
            sport, created = Sport.objects.get_or_create(name=sport_name)
            created_sports[sport_name] = sport
            if created:
                sports_count += 1

        # Теперь создаем категории для видов спорта
        # По модели SportCategory требует sport, поэтому создаем категорию для каждого вида спорта
        categories_mapping = {
            'Игровые': ['Футбол', 'Баскетбол', 'Волейбол', 'Хоккей', 'Теннис'],
            'Единоборства': ['Дзюдо', 'Карате', 'Бокс', 'Борьба', 'Тхэквондо'],
            'Водные': ['Плавание', 'Водное поло', 'Прыжки в воду'],
            'Легкая атлетика': ['Бег', 'Прыжки', 'Метание', 'Многоборье'],
            'Гимнастика': ['Художественная гимнастика', 'Спортивная гимнастика'],
            'Зимние': ['Лыжи', 'Коньки', 'Биатлон'],
        }

        categories_count = 0
        for category_name, sport_names in categories_mapping.items():
            for sport_name in sport_names:
                if sport_name in created_sports:
                    sport = created_sports[sport_name]
                    try:
                        category, created = SportCategory.objects.get_or_create(
                            sport=sport,
                            name=category_name
                        )
                        if created:
                            categories_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Не удалось создать категорию {category_name} для {sport_name}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'✓ Создано {sports_count} видов спорта и {categories_count} категорий'))

    def create_users(self):
        """Создание пользователей с разными ролями"""
        self.stdout.write('Создание пользователей...')
        
        from apps.users.models import UserRole
        from apps.athletes.models import AthleteProfile
        from apps.coaches.models import CoachProfile
        from apps.parents.models import ParentProfile
        from apps.geography.models import City
        from apps.sports.models import Sport

        cities = list(City.objects.all())
        sports = list(Sport.objects.all())

        # Спортсмены
        athletes_data = [
            ('athlete1@test.ru', 'Иванов', 'Иван', 'Иванович', '2005-05-15', 'athlete'),
            ('athlete2@test.ru', 'Петров', 'Петр', 'Петрович', '2006-08-20', 'athlete'),
            ('athlete3@test.ru', 'Сидоров', 'Сидор', 'Сидорович', '2007-03-10', 'athlete'),
        ]

        for email, last_name, first_name, patronymic, birth_date, role in athletes_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'patronymic': patronymic,
                    'birth_date': birth_date,
                    'phone': f'+7{random.randint(9000000000, 9999999999)}',
                    'city': random.choice(cities).name if cities else '',
                }
            )
            if created:
                user.set_password('test123')
                user.save()
                UserRole.objects.create(user=user, role=role)
                
                if role == 'athlete' and cities and sports:
                    try:
                        AthleteProfile.objects.create(
                            user=user,
                            city=random.choice(cities),
                            main_sport=random.choice(sports),
                            health_group='I',
                            goals=['ЗОЖ', 'Соревнования']
                        )
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Не удалось создать профиль спортсмена: {e}'))

        # Тренеры
        coaches_data = [
            ('coach1@test.ru', 'Тренеров', 'Алексей', 'Александрович', 'coach'),
            ('coach2@test.ru', 'Наставников', 'Дмитрий', 'Дмитриевич', 'coach'),
        ]

        for email, last_name, first_name, patronymic, role in coaches_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'patronymic': patronymic,
                    'phone': f'+7{random.randint(9000000000, 9999999999)}',
                    'city': random.choice(cities).name if cities else '',
                }
            )
            if created:
                user.set_password('test123')
                user.save()
                UserRole.objects.create(user=user, role=role)
                
                if role == 'coach' and cities and sports:
                    try:
                        CoachProfile.objects.create(
                            user=user,
                            city=random.choice(cities),
                            specialization=random.choice(sports),
                            experience_years=random.randint(3, 15)
                        )
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Не удалось создать профиль тренера: {e}'))

        # Родители
        parents_data = [
            ('parent1@test.ru', 'Родителев', 'Мария', 'Ивановна', 'parent'),
            ('parent2@test.ru', 'Материнская', 'Елена', 'Петровна', 'parent'),
        ]

        for email, last_name, first_name, patronymic, role in parents_data:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'patronymic': patronymic,
                    'phone': f'+7{random.randint(9000000000, 9999999999)}',
                    'city': random.choice(cities).name if cities else '',
                }
            )
            if created:
                user.set_password('test123')
                user.save()
                UserRole.objects.create(user=user, role=role)
                ParentProfile.objects.create(user=user)

        self.stdout.write(self.style.SUCCESS('✓ Пользователи созданы'))

    def create_organizations(self):
        """Создание спортивных организаций"""
        self.stdout.write('Создание организаций...')
        
        from apps.organizations.models import Organization, SportDirection
        from apps.geography.models import City
        from apps.sports.models import Sport
        from apps.users.models import UserRole

        cities = list(City.objects.all())
        sports = list(Sport.objects.all())

        organizations_data = [
            ('ДЮСШ "Олимпиец"', 'state', 'Уфа', ['Футбол', 'Баскетбол', 'Волейбол']),
            ('Спортивный клуб "Чемпион"', 'private', 'Стерлитамак', ['Бокс', 'Дзюдо', 'Карате']),
            ('ДЮСШ по плаванию', 'state', 'Салават', ['Плавание', 'Водное поло']),
            ('Центр развития спорта', 'state', 'Нефтекамск', ['Теннис', 'Легкая атлетика']),
            ('Спортивная школа "Юность"', 'state', 'Октябрьский', ['Художественная гимнастика', 'Спортивная гимнастика']),
        ]

        org_count = 0
        for name, org_type, city_name, sport_names in organizations_data:
            city = next((c for c in cities if c.name == city_name), cities[0] if cities else None)
            
            org, created = Organization.objects.get_or_create(
                name=name,
                defaults={
                    'org_type': org_type,
                    'city': city,
                    'address': f'{city.name}, ул. Спортивная, д. {random.randint(1, 100)}',
                    'inn': f'{random.randint(1000000000, 9999999999)}',
                    'status': 'approved',
                    'verified_at': timezone.now(),
                }
            )
            
            if created:
                org_count += 1
                # Добавляем виды спорта
                for sport_name in sport_names:
                    sport = next((s for s in sports if s.name == sport_name), None)
                    if sport:
                        SportDirection.objects.get_or_create(
                            organization=org,
                            sport=sport
                        )

        self.stdout.write(self.style.SUCCESS(f'✓ Создано {org_count} организаций'))

    def create_events(self):
        """Создание мероприятий"""
        self.stdout.write('Создание мероприятий...')
        
        from apps.events.models import Event, EventCategory, EventAgeGroup
        from apps.geography.models import City
        from apps.organizations.models import Organization
        from apps.sports.models import Sport

        cities = list(City.objects.all())
        organizations = list(Organization.objects.filter(status='approved'))
        sports = list(Sport.objects.all())

        if not cities or not sports:
            self.stdout.write(self.style.WARNING('Недостаточно данных для создания мероприятий'))
            return

        events_data = [
            ('Республиканский турнир по футболу', 'competition', 'republic', 'Уфа', 'Стадион "Динамо"', 30),
            ('Городские соревнования по плаванию', 'competition', 'city', 'Стерлитамак', 'Бассейн "Волна"', 20),
            ('Фестиваль ГТО', 'gto_festival', 'city', 'Салават', 'Стадион "Нефтехимик"', 25),
            ('Открытый турнир по боксу', 'competition', 'city', 'Нефтекамск', 'Дворец спорта', 18),
            ('Спортивный лагерь "Олимпийские надежды"', 'camp', 'republic', 'Уфа', 'База отдыха "Родник"', 35),
        ]

        event_count = 0
        for title, event_type, level, city_name, venue, days_ahead in events_data:
            city = next((c for c in cities if c.name == city_name), cities[0])
            start_date = timezone.now() + timedelta(days=days_ahead)
            end_date = start_date + timedelta(days=1)

            # Создаем категорию события
            sport = random.choice(sports)
            category, _ = EventCategory.objects.get_or_create(
                name=f'{sport.name} - {title}',
                defaults={'sport': sport}
            )

            event, created = Event.objects.get_or_create(
                title=title,
                defaults={
                    'description': f'Описание мероприятия: {title}. Приглашаем всех желающих принять участие!',
                    'event_type': event_type,
                    'level': level,
                    'city': city,
                    'venue': venue,
                    'start_date': start_date,
                    'end_date': end_date,
                    'organizer_org': random.choice(organizations) if organizations else None,
                    'requires_registration': True,
                    'status': 'published',
                }
            )

            if created:
                event_count += 1
                # Добавляем возрастные группы
                age_groups = [
                    (8, 12),
                    (13, 16),
                    (17, 20),
                ]
                for min_age, max_age in age_groups:
                    EventAgeGroup.objects.create(
                        event=event,
                        min_age=min_age,
                        max_age=max_age
                    )

        self.stdout.write(self.style.SUCCESS(f'✓ Создано {event_count} мероприятий'))
