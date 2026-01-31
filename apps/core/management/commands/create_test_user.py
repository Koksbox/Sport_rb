# apps/core/management/commands/create_test_user.py
"""
Команда для создания тестового пользователя
Использование: python manage.py create_test_user
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import UserRole
from apps.geography.models import Region, City
from apps.sports.models import Sport
from apps.athletes.models import AthleteProfile
from apps.parents.models import ParentProfile
from apps.users.models import Consent

User = get_user_model()


class Command(BaseCommand):
    help = 'Создаёт тестового пользователя с указанными данными'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Создание тестового пользователя...'))
        
        # Данные пользователя
        email = 'edgarvaliev463@xmail.com'
        password = 'qwqwqw12'
        full_name = 'Валиев Эдгар Альбертович'
        phone = '89191597306'
        city_name = 'Стерлитамак'
        
        # Разбиваем ФИО на части
        name_parts = full_name.split()
        if len(name_parts) < 2:
            self.stdout.write(self.style.ERROR('Ошибка: ФИО должно содержать минимум Фамилию и Имя'))
            return
        
        last_name = name_parts[0]
        first_name = name_parts[1]
        patronymic = name_parts[2] if len(name_parts) > 2 else ''
        
        # Создаём или получаем регион
        region, _ = Region.objects.get_or_create(name='Республика Башкортостан')
        
        # Создаём или получаем город
        city, _ = City.objects.get_or_create(
            name=city_name,
            region=region,
            defaults={'settlement_type': 'city'}
        )
        
        # Создаём или получаем вид спорта (для профиля спортсмена)
        sport, _ = Sport.objects.get_or_create(name='Футбол')
        
        # Проверяем, существует ли пользователь
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            self.stdout.write(self.style.WARNING(f'Пользователь уже существует: {email}'))
            
            # Обновляем данные (проверяем телефон на уникальность)
            user.first_name = first_name
            user.last_name = last_name
            user.patronymic = patronymic
            # Обновляем телефон только если он не занят другим пользователем
            if not User.objects.filter(phone=phone).exclude(id=user.id).exists():
                user.phone = phone
            user.city = city_name
            user.set_password(password)
            user.save()
            
            self.stdout.write(self.style.SUCCESS('Данные пользователя обновлены'))
        else:
            # Создаём пользователя
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                patronymic=patronymic,
                phone=phone,
                city=city_name
            )
            
            self.stdout.write(self.style.SUCCESS(f'Пользователь создан: {email}'))
        
        # Создаём согласие на обработку ПДн
        Consent.objects.get_or_create(
            user=user,
            type='personal_data',
            defaults={'granted': True}
        )
        
        # Создаём роли (с автоматической генерацией unique_id)
        roles_to_create = ['athlete', 'parent']
        
        for role_name in roles_to_create:
            role, created = UserRole.objects.get_or_create(
                user=user,
                role=role_name,
                defaults={'is_active': True}
            )
            
            # Убеждаемся, что unique_id сгенерирован
            if not role.unique_id:
                import random
                import string
                while True:
                    unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    if not UserRole.objects.filter(unique_id=unique_id).exists():
                        role.unique_id = unique_id
                        role.save()
                        break
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Роль "{role_name}" создана (ID: {role.unique_id})'))
            else:
                self.stdout.write(self.style.SUCCESS(f'  Роль "{role_name}" уже существует (ID: {role.unique_id})'))
        
        # Создаём профиль спортсмена
        athlete_profile, created = AthleteProfile.objects.get_or_create(
            user=user,
            defaults={
                'city': city,
                'main_sport': sport
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  Профиль спортсмена создан'))
        else:
            self.stdout.write(self.style.SUCCESS('  Профиль спортсмена уже существует'))
        
        # Создаём профиль родителя
        parent_profile, created = ParentProfile.objects.get_or_create(user=user)
        
        if created:
            self.stdout.write(self.style.SUCCESS('  Профиль родителя создан'))
        else:
            self.stdout.write(self.style.SUCCESS('  Профиль родителя уже существует'))
        
        # Выводим информацию
        self.stdout.write(self.style.SUCCESS('\n✓ Тестовый пользователь готов!'))
        self.stdout.write(self.style.SUCCESS(f'\nДанные для входа:'))
        self.stdout.write(self.style.SUCCESS(f'  Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'  Пароль: {password}'))
        self.stdout.write(self.style.SUCCESS(f'  ФИО: {full_name}'))
        self.stdout.write(self.style.SUCCESS(f'  Телефон: {phone}'))
        self.stdout.write(self.style.SUCCESS(f'  Город: {city_name}'))
        
        # Выводим ID ролей
        roles = UserRole.objects.filter(user=user)
        if roles.exists():
            self.stdout.write(self.style.SUCCESS(f'\nID ролей:'))
            for role in roles:
                role_display = role.get_role_display() if hasattr(role, 'get_role_display') else role.role
                self.stdout.write(self.style.SUCCESS(f'  {role_display}: {role.unique_id}'))
