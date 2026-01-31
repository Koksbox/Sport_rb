# apps/core/management/commands/reset_all_data.py
"""
Команда для полной очистки базы данных (включая всех пользователей)
Использование: python manage.py reset_all_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Полностью очищает базу данных (включая всех пользователей)'

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
            with transaction.atomic():
                self.stdout.write(self.style.SUCCESS('Начинаем полную очистку базы данных...'))
                self.clear_all_data()
                
                self.stdout.write(self.style.SUCCESS('✓ База данных полностью очищена!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))
            import traceback
            traceback.print_exc()

    def clear_all_data(self):
        """Полная очистка всех данных из базы"""
        from apps.organizations.models import Organization
        from apps.sports.models import Sport, SportCategory
        from apps.geography.models import City, Region, District
        from apps.events.models import Event, EventCategory, EventAgeGroup
        from apps.achievements.models import Achievement
        from apps.notifications.models import Notification, NotificationSubscription, NotificationTemplate
        from apps.audit.models import AuditLog
        from apps.athletes.models import AthleteProfile
        from apps.coaches.models import CoachProfile
        from apps.parents.models import ParentProfile, ParentChildLink
        from apps.users.models import UserRole, Consent
        from apps.authn.models import AuthProvider
        from apps.attendance.models import AttendanceRecord
        from apps.training.models import TrainingGroup
        from apps.organizations.staff.coach_membership import CoachMembership
        from apps.city_committee.models import CommitteeStaff, CityPermission, ManagedEvent, CommitteeRegistrationCode
        from apps.core.models import ContactMessage
        from apps.events.models import EventRegistration, EventInvitation
        
        # Удаляем в правильном порядке (сначала зависимые, потом основные)
        self.stdout.write('  Удаление регистраций на мероприятия...')
        EventRegistration.objects.all().delete()
        
        self.stdout.write('  Удаление приглашений на мероприятия...')
        EventInvitation.objects.all().delete()
        
        # Удаление сообщений обратной связи (если таблица существует)
        try:
            self.stdout.write('  Удаление сообщений обратной связи...')
            ContactMessage.objects.all().delete()
        except Exception:
            pass  # Таблица может не существовать
        
        self.stdout.write('  Удаление подписок на уведомления...')
        NotificationSubscription.objects.all().delete()
        
        self.stdout.write('  Удаление шаблонов уведомлений...')
        NotificationTemplate.objects.all().delete()
        
        self.stdout.write('  Удаление уведомлений...')
        Notification.objects.all().delete()
        
        self.stdout.write('  Удаление аудит-логов...')
        AuditLog.objects.all().delete()
        
        self.stdout.write('  Удаление достижений...')
        Achievement.objects.all().delete()
        
        self.stdout.write('  Удаление посещаемости...')
        AttendanceRecord.objects.all().delete()
        
        self.stdout.write('  Удаление тренировочных групп...')
        TrainingGroup.objects.all().delete()
        
        self.stdout.write('  Удаление связей родитель-ребёнок...')
        ParentChildLink.objects.all().delete()
        
        self.stdout.write('  Удаление членств тренеров...')
        CoachMembership.objects.all().delete()
        
        self.stdout.write('  Удаление мероприятий...')
        Event.objects.all().delete()
        EventCategory.objects.all().delete()
        EventAgeGroup.objects.all().delete()
        
        self.stdout.write('  Удаление организаций...')
        Organization.objects.all().delete()
        
        # Удаление данных спорткомитета (если таблицы существуют)
        try:
            self.stdout.write('  Удаление кодов регистрации спорткомитета...')
            CommitteeRegistrationCode.objects.all().delete()
        except Exception:
            pass
        
        try:
            self.stdout.write('  Удаление прав доступа спорткомитета...')
            CityPermission.objects.all().delete()
        except Exception:
            pass
        
        try:
            self.stdout.write('  Удаление управляемых мероприятий...')
            ManagedEvent.objects.all().delete()
        except Exception:
            pass
        
        try:
            self.stdout.write('  Удаление сотрудников спорткомитета...')
            CommitteeStaff.objects.all().delete()
        except Exception:
            pass
        
        self.stdout.write('  Удаление профилей...')
        AthleteProfile.objects.all().delete()
        CoachProfile.objects.all().delete()
        ParentProfile.objects.all().delete()
        
        self.stdout.write('  Удаление ролей...')
        UserRole.objects.all().delete()
        
        self.stdout.write('  Удаление согласий...')
        Consent.objects.all().delete()
        
        self.stdout.write('  Удаление провайдеров авторизации...')
        AuthProvider.objects.all().delete()
        
        self.stdout.write('  Удаление пользователей...')
        User.objects.all().delete()
        
        self.stdout.write('  Удаление видов спорта...')
        Sport.objects.all().delete()
        SportCategory.objects.all().delete()
        
        self.stdout.write('  Удаление городов и районов...')
        District.objects.all().delete()
        City.objects.all().delete()
        Region.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('  ✓ Все данные удалены'))
